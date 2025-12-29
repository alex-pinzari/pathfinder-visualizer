# backend/pathfinding/osm/routing.py
from __future__ import annotations

from typing import Dict, Any, List, Tuple
import time
import osmnx as ox

from pathfinding.osm.graph_adapter import OSMGraphAdapter
from pathfinding.graph.dijkstra_graph import dijkstra_graph
from pathfinding.graph.astar_graph import astar_graph


def _nearest_node(G, lat: float, lon: float) -> int:
    return int(ox.distance.nearest_nodes(G, X=lon, Y=lat))


def _nodes_to_latlon(adapter: OSMGraphAdapter, nodes: List[int]) -> List[List[float]]:
    # [[lat, lon], ...]
    return [[adapter.to_latlon(n)[0], adapter.to_latlon(n)[1]] for n in nodes]


def _edge_polyline_latlon(G, u: int, v: int, max_points: int = 120) -> List[List[float]]:
    """
    Return a polyline for edge (u -> v) using OSM geometry if present.
    Output: [[lat, lon], [lat, lon], ...]

    max_points downsamples geometry to keep payload sane for big searches.
    """
    data = G.get_edge_data(u, v)
    if not data:
        # fallback straight line between nodes if edge missing
        uy = G.nodes[u]["y"]
        ux = G.nodes[u]["x"]
        vy = G.nodes[v]["y"]
        vx = G.nodes[v]["x"]
        return [[float(uy), float(ux)], [float(vy), float(vx)]]

    # choose "best" parallel edge: shortest length
    best_key = min(data.keys(), key=lambda k: data[k].get("length", float("inf")))
    attr = data[best_key]
    geom = attr.get("geometry")

    if geom is not None:
        # shapely LineString coords are (x=lon, y=lat)
        coords = list(geom.coords)
        if len(coords) <= max_points:
            return [[float(lat), float(lon)] for lon, lat in coords]

        # downsample evenly to max_points
        step = max(1, len(coords) // max_points)
        sampled = coords[::step]
        if sampled[-1] != coords[-1]:
            sampled.append(coords[-1])
        return [[float(lat), float(lon)] for lon, lat in sampled]

    # fallback to node-to-node straight segment
    uy = G.nodes[u]["y"]
    ux = G.nodes[u]["x"]
    vy = G.nodes[v]["y"]
    vx = G.nodes[v]["x"]
    return [[float(uy), float(ux)], [float(vy), float(vx)]]


def _edges_to_polylines(
    G,
    edges: List[Tuple[int, int]],
    max_edges: int = 20000,
    max_points_per_edge: int = 120
) -> List[List[List[float]]]:
    """
    Convert explored edges into a list of polylines.

    max_edges prevents blowing up payload size on huge searches.
    max_points_per_edge downsamples each geometry polyline.
    """
    if len(edges) > max_edges:
        edges = edges[:max_edges]

    out: List[List[List[float]]] = []
    for u, v in edges:
        out.append(_edge_polyline_latlon(G, int(u), int(v), max_points=max_points_per_edge))
    return out


def route_compare_own(
    G,
    start_lat: float,
    start_lon: float,
    goal_lat: float,
    goal_lon: float
) -> Dict[str, Any]:
    """
    Runs Dijkstra and A* on the SAME OSM graph and returns:
    - final path polyline for each
    - explored road segments polyline for each (for animation)
    - metrics (distance, runtime, counts)
    """
    adapter = OSMGraphAdapter(G)

    s = _nearest_node(G, start_lat, start_lon)
    g = _nearest_node(G, goal_lat, goal_lon)

    graph_nodes_count = int(getattr(G, "number_of_nodes", lambda: 0)())
    graph_edges_count = int(getattr(G, "number_of_edges", lambda: 0)())

    # --- Dijkstra ---
    t0 = time.perf_counter()
    d_path_nodes, d_visited_nodes, d_dist, d_found, d_came_from, d_explored_edges = dijkstra_graph(adapter, s, g)
    t1 = time.perf_counter()

    # --- A* ---
    t2 = time.perf_counter()
    a_path_nodes, a_visited_nodes, a_dist, a_found, a_came_from, a_explored_edges = astar_graph(adapter, s, g)
    t3 = time.perf_counter()

    # convert path nodes to lat/lon (for final route)
    d_path = _nodes_to_latlon(adapter, d_path_nodes)
    a_path = _nodes_to_latlon(adapter, a_path_nodes)

    # convert explored edges to exact road segments (polylines)
    d_explored = _edges_to_polylines(G, d_explored_edges)
    a_explored = _edges_to_polylines(G, a_explored_edges)

    return {
        "dijkstra": {
            "path": d_path,
            "explored_edges": d_explored,
            "distance_m": float(d_dist),
            "runtime_ms": (t1 - t0) * 1000.0,
            "visited_count": int(len(d_visited_nodes)),
            "path_nodes_count": int(len(d_path_nodes)),
            "explored_edges_count": int(len(d_explored_edges)),
            "found": bool(d_found),
        },
        "astar": {
            "path": a_path,
            "explored_edges": a_explored,
            "distance_m": float(a_dist),
            "runtime_ms": (t3 - t2) * 1000.0,
            "visited_count": int(len(a_visited_nodes)),
            "path_nodes_count": int(len(a_path_nodes)),
            "explored_edges_count": int(len(a_explored_edges)),
            "found": bool(a_found),
        },
        "meta": {
            "start_node": int(s),
            "goal_node": int(g),
            "graph_nodes_count": graph_nodes_count,
            "graph_edges_count": graph_edges_count,
        },
    }