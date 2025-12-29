from __future__ import annotations

import heapq
from typing import Dict, List, Tuple

from .grid import Grid, Coord


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from: Dict[Coord, Coord], start: Coord, goal: Coord) -> List[Coord]:
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


def astar(grid: Grid, start: Coord, goal: Coord):
    """
    A* on a 4-neighbor grid with unit costs.

    Returns: (visited_order, path, found)
      visited_order: nodes expanded (no duplicates, skips stale PQ entries)
      path: list of coords from start..goal (inclusive) or [] if not found
      found: bool
    """
    if start == goal:
        return [start], [start], True

    # Heap item: (f, g, coord)
    open_heap: List[Tuple[float, float, Coord]] = []
    start_f = float(manhattan(start, goal))
    heapq.heappush(open_heap, (start_f, 0.0, start))

    came_from: Dict[Coord, Coord] = {}
    g_score: Dict[Coord, float] = {start: 0.0}

    # Used to skip stale heap entries
    best_f: Dict[Coord, float] = {start: start_f}

    visited_order: List[Coord] = []
    visited_set = set()

    while open_heap:
        f, g, cur = heapq.heappop(open_heap)

        # skip outdated entries
        if best_f.get(cur, float("inf")) != f:
            continue

        if cur not in visited_set:
            visited_set.add(cur)
            visited_order.append(cur)

        if cur == goal:
            path = reconstruct_path(came_from, start, goal)
            return visited_order, path, True

        for nxt in grid.neighbors(cur):
            tentative_g = g + 1.0  # unit step

            if tentative_g < g_score.get(nxt, float("inf")):
                came_from[nxt] = cur
                g_score[nxt] = tentative_g

                nxt_f = tentative_g + manhattan(nxt, goal)

                # only push if this improves best known f for nxt
                if nxt_f < best_f.get(nxt, float("inf")):
                    best_f[nxt] = float(nxt_f)
                    heapq.heappush(open_heap, (float(nxt_f), float(tentative_g), nxt))

    return visited_order, [], False