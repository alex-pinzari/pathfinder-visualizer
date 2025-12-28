from typing import List, Tuple, Dict
import heapq

from .grid import Grid

Coord = Tuple[int, int]


def reconstruct_path(came_from: Dict[Coord, Coord], start: Coord, goal: Coord) -> List[Coord]:
    """
    Rebuilds the path from start to goal using the came_from map.
    If no path, returns empty list.
    """
    if goal not in came_from and goal != start:
        return []

    cur = goal
    path = [cur]
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path


def dijkstra(grid: Grid, start: Coord, goal: Coord):
    dist: Dict[Coord, int] = {start: 0}
    came_from: Dict[Coord, Coord] = {}
    visited_order: List[Coord] = []

    pq: List[Tuple[int, Coord]] = []
    heapq.heappush(pq, (0, start))

    processed = set()  # nodes we already finalized (for clean visualization)

    while pq:
        current_dist, current = heapq.heappop(pq)

        # skip outdated entries
        if current_dist != dist.get(current, None):
            continue

        # log only once
        if current in processed:
            continue
        processed.add(current)
        visited_order.append(current)

        if current == goal:
            break

        for neighbor in grid.neighbors(current):
            new_dist = current_dist + 1
            if new_dist < dist.get(neighbor, 10**18):
                dist[neighbor] = new_dist
                came_from[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    path = reconstruct_path(came_from, start, goal)
    return path, visited_order
