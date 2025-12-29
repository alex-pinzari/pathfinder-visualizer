# backend/pathfinding/osm/graph_adapter.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple, Dict
import osmnx as ox


NodeId = int
LatLon = Tuple[float, float]


@dataclass(frozen=True)
class OSMGraphAdapter:
    """
    Wraps an OSMnx MultiDiGraph so algorithms can call:
      - neighbors(u) -> list[(v, cost_meters)]
      - heuristic(u, goal) -> meters
      - to_latlon(u) -> (lat, lon)
    """
    G: object

    def neighbors(self, u: NodeId) -> List[Tuple[NodeId, float]]:
        out: List[Tuple[NodeId, float]] = []

        # MultiDiGraph adjacency: G[u] is dict[v] -> dict[key] -> edge_attr
        for v, key_dict in self.G[u].items():
            best = None
            for _k, attrs in key_dict.items():
                length = attrs.get("length", None)
                if length is None:
                    continue
                length = float(length)
                if best is None or length < best:
                    best = length
            if best is not None:
                out.append((int(v), best))

        return out

    def to_latlon(self, u: NodeId) -> LatLon:
        n = self.G.nodes[u]
        return (float(n["y"]), float(n["x"]))  # (lat, lon)

    def heuristic_m(self, u: NodeId, goal: NodeId) -> float:
        # straight-line distance in meters
        uy, ux = self.to_latlon(u)
        gy, gx = self.to_latlon(goal)
        # great_circle returns meters
        return float(ox.distance.great_circle(uy, ux, gy, gx))