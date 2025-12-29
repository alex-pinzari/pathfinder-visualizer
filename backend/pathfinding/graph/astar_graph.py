# backend/pathfinding/astar_graph.py
from __future__ import annotations

import heapq
from typing import Dict, List, Tuple

from pathfinding.osm.graph_adapter import OSMGraphAdapter, NodeId


def reconstruct_path_nodes(came_from: Dict[NodeId, NodeId], start: NodeId, goal: NodeId) -> List[NodeId]:
    if start == goal:
        return [start]
    if goal not in came_from:
        return []

    cur = goal
    path = [cur]
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path


def astar_graph(
    adapter: OSMGraphAdapter,
    start: NodeId,
    goal: NodeId
) -> Tuple[List[NodeId], List[NodeId], float, bool, Dict[NodeId, NodeId], List[Tuple[NodeId, NodeId]]]:
    """
    Returns:
      (path_nodes, visited_order, distance_m, found, came_from, explored_edges)

    visited_order   = nodes expanded (no duplicates)
    explored_edges  = list of (u, v) edges that improved g_score[v] (relaxations)
                    = good proxy for "roads explored" (chronological)
    """
    if start == goal:
        return [start], [start], 0.0, True, {}, []

    open_heap: List[Tuple[float, float, NodeId]] = []  # (f, g, node)

    g_score: Dict[NodeId, float] = {start: 0.0}
    came_from: Dict[NodeId, NodeId] = {}
    explored_edges: List[Tuple[NodeId, NodeId]] = []

    start_h = adapter.heuristic_m(start, goal)
    start_f = start_h
    heapq.heappush(open_heap, (start_f, 0.0, start))

    best_f: Dict[NodeId, float] = {start: start_f}

    visited_order: List[NodeId] = []
    visited_set = set()

    while open_heap:
        f, g, u = heapq.heappop(open_heap)

        # skip stale
        if best_f.get(u, float("inf")) != f:
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
                explored_edges.append((u, v))  # <-- this is what we will draw as explored roads

                h = adapter.heuristic_m(v, goal)
                nxt_f = tentative_g + h

                if nxt_f < best_f.get(v, float("inf")):
                    best_f[v] = float(nxt_f)
                    heapq.heappush(open_heap, (float(nxt_f), float(tentative_g), v))

    return [], visited_order, float("inf"), False, came_from, explored_edges