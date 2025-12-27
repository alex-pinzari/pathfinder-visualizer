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
    """
    Classic Dijkstra on a grid with cost 1 per move.

    Returns:
        path: list of coords (r, c) from start to goal
        visited_order: list of coords in the order they were popped from the queue
                       (useful for visualization)
    """
    # Distance from start to this node
    dist: Dict[Coord, int] = {start: 0}
    # For reconstructing path
    came_from: Dict[Coord, Coord] = {}
    # For visualization (the order in which cells are processed)
    visited_order: List[Coord] = []

    # Priority queue of (distance_so_far, node)
    pq: List[Tuple[int, Coord]] = []
    heapq.heappush(pq, (0, start))

    while pq:
        current_dist, current = heapq.heappop(pq)
        visited_order.append(current)

        # If we've reached the goal, we can stop
        if current == goal:
            break

        # If this entry is outdated, skip it
        if current_dist > dist[current]:
            continue

        # Explore neighbors
        for neighbor in grid.neighbors(current):
            new_dist = current_dist + 1  # each move costs 1
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                came_from[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    path = reconstruct_path(came_from, start, goal)
    return path, visited_order
