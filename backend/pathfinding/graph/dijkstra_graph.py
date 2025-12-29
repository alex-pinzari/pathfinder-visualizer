# backend/pathfinding/dijkstra_graph.py
from __future__ import annotations

from typing import Dict, List, Tuple
import heapq

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


def dijkstra_graph(
    adapter: OSMGraphAdapter,
    start: NodeId,
    goal: NodeId
) -> Tuple[List[NodeId], List[NodeId], float, Dict[NodeId, NodeId], List[Tuple[NodeId, NodeId]]]:
    """
    Returns:
      (path_nodes, visited_order, distance_m, came_from, explored_edges)

    visited_order   = nodes finalized/popped (no duplicates)
    explored_edges  = list of (u, v) edges that actually improved dist[v] (relaxations)
                    = good proxy for "roads explored" (in chronological order)
    """
    dist: Dict[NodeId, float] = {start: 0.0}
    came_from: Dict[NodeId, NodeId] = {}
    visited_order: List[NodeId] = []
    explored_edges: List[Tuple[NodeId, NodeId]] = []

    pq: List[Tuple[float, NodeId]] = []
    heapq.heappush(pq, (0.0, start))

    processed = set()

    while pq:
        current_dist, u = heapq.heappop(pq)

        # skip stale entries
        if current_dist != dist.get(u, None):
            continue

        if u in processed:
            continue
        processed.add(u)
        visited_order.append(u)

        if u == goal:
            break

        for v, cost in adapter.neighbors(u):
            new_dist = current_dist + cost
            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                came_from[v] = u
                explored_edges.append((u, v))  # <-- this is what we will draw as explored roads
                heapq.heappush(pq, (new_dist, v))

    path_nodes = reconstruct_path_nodes(came_from, start, goal)
    return path_nodes, visited_order, dist.get(goal, float("inf")), came_from, explored_edges