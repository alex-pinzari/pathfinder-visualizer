from typing import List, Tuple

Coord = Tuple[int, int]


class Grid:
    def __init__(self, cells: List[List[int]]):
        """
        cells: 2D list of ints
        0 = free cell (walkable)
        1 = wall (blocked)
        """
        self.cells = cells
        self.height = len(cells)
        self.width = len(cells[0]) if self.height > 0 else 0

    def in_bounds(self, pos: Coord) -> bool:
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def is_walkable(self, pos: Coord) -> bool:
        r, c = pos
        # 0 = free, 1 = wall
        return self.cells[r][c] == 0

    def neighbors(self, pos: Coord):
        """
        Returns all valid, walkable neighbors of pos (up, down, left, right)
        """
        r, c = pos
        candidates = [
            (r - 1, c),  # up
            (r + 1, c),  # down
            (r, c - 1),  # left
            (r, c + 1),  # right
        ]
        for nxt in candidates:
            if self.in_bounds(nxt) and self.is_walkable(nxt):
                yield nxt
