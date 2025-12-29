# backend/pathfinding/utils.py
from __future__ import annotations

from typing import Dict, List

from pathfinding.osm.graph_adapter import NodeId


def reconstruct_path_nodes(came_from: Dict[NodeId, NodeId], start: NodeId, goal: NodeId) -> List[NodeId]:
    """
    Reconstruct path from start -> goal using came_from map.
    Returns [] if goal unreachable (and start != goal).
    """
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