# backend/osm/graph_cache.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import threading
import osmnx as ox

# OSMnx can be chatty; optional:
ox.settings.log_console = False
ox.settings.use_cache = True

@dataclass(frozen=True)
class GraphKey:
    place: str
    network: str  # "drive", "walk", "bike", ...

_graph_lock = threading.Lock()
_graphs: Dict[GraphKey, object] = {}


def get_graph(place: str, network: str):
    """
    Returns a cached OSMnx graph for a place + network type.
    Caches in-memory so repeated requests are fast.
    """
    key = GraphKey(place=place.strip(), network=network.strip())

    with _graph_lock:
        if key in _graphs:
            return _graphs[key]

    # Download/build graph outside lock to avoid blocking other keys too long
    G = ox.graph_from_place(key.place, network_type=key.network, simplify=True)

    # Add edge lengths (meters)
    G = ox.distance.add_edge_lengths(G)

    with _graph_lock:
        _graphs[key] = G

    return G