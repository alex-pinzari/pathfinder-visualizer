# backend/pathfinding/astar_graph.py
from __future__ import annotations

import heapq
from typing import Dict, List, Tuple

from pathfinding.osm.graph_adapter import OSMGraphAdapter, NodeId
from pathfinding.utils import reconstruct_path_nodes


def astar_graph(
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

    visited_order  = nodes expanded (no duplicates)
    explored_edges = list of (u, v) edges that improved g_score[v] (relaxations)
    """
    if start == goal:
        return [start], [start], 0.0, True, {}, []

    # heap items: (f, g, node)
    open_heap: List[Tuple[float, float, NodeId]] = []
    heapq.heappush(open_heap, (adapter.heuristic_m(start, goal), 0.0, start))

    g_score: Dict[NodeId, float] = {start: 0.0}
    came_from: Dict[NodeId, NodeId] = {}
    explored_edges: List[Tuple[NodeId, NodeId]] = []

    visited_order: List[NodeId] = []
    visited_set = set()

    while open_heap:
        f, g, u = heapq.heappop(open_heap)

        # Skip stale heap entries: only process if this is the current best g for u
        if g != g_score.get(u, float("inf")):
            continue

        if u not in visited_set:
            visited_set.add(u)
            visited_order.append(u)

        if u == goal:
            path_nodes = reconstruct_path_nodes(came_from, start, goal)
            return path_nodes, visited_order, g, True, came_from, explored_edges

        for v, cost in adapter.neighbors(u):
            tentative_g = g + cost
            if tentative_g < g_score.get(v, float("inf")):
                came_from[v] = u
                g_score[v] = tentative_g
                explored_edges.append((u, v))

                h = adapter.heuristic_m(v, goal)
                nxt_f = tentative_g + h
                heapq.heappush(open_heap, (float(nxt_f), float(tentative_g), v))

    return [], visited_order, float("inf"), False, came_from, explored_edges