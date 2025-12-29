# backend/pathfinding/dijkstra_graph.py
from __future__ import annotations

import heapq
from typing import Dict, List, Tuple

from pathfinding.osm.graph_adapter import OSMGraphAdapter, NodeId
from pathfinding.utils import reconstruct_path_nodes


def dijkstra_graph(
    adapter: OSMGraphAdapter,
    start: NodeId,
    goal: NodeId
) -> Tuple[
    List[NodeId],                 # path_nodes
    List[NodeId],                 # visited_order
    float,                        # distance_m
    bool,                         # found
    Dict[NodeId, NodeId],         # came_from
    List[Tuple[NodeId, NodeId]]   # explored_edges
]:
    """
    Returns:
      (path_nodes, visited_order, distance_m, found, came_from, explored_edges)

    visited_order  = nodes finalized/popped (no duplicates)
    explored_edges = list of (u, v) edges that improved dist[v] (relaxations)
    """
    if start == goal:
        return [start], [start], 0.0, True, {}, []

    dist: Dict[NodeId, float] = {start: 0.0}
    came_from: Dict[NodeId, NodeId] = {}
    visited_order: List[NodeId] = []
    explored_edges: List[Tuple[NodeId, NodeId]] = []

    pq: List[Tuple[float, NodeId]] = []
    heapq.heappush(pq, (0.0, start))

    visited_set = set()

    while pq:
        current_dist, u = heapq.heappop(pq)

        # Skip stale heap entries (avoid float equality traps)
        if current_dist > dist.get(u, float("inf")):
            continue

        if u in visited_set:
            continue
        visited_set.add(u)
        visited_order.append(u)

        if u == goal:
            break

        for v, cost in adapter.neighbors(u):
            new_dist = current_dist + cost
            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                came_from[v] = u
                explored_edges.append((u, v))
                heapq.heappush(pq, (float(new_dist), v))

    distance_m = dist.get(goal, float("inf"))
    found = distance_m != float("inf")
    path_nodes = reconstruct_path_nodes(came_from, start, goal)

    return path_nodes, visited_order, distance_m, found, came_from, explored_edges