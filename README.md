# Real-World Pathfinding: Dijkstra vs A*

This project benchmarks **Dijkstra** and **A\*** on **real city road networks** using OpenStreetMap data.

Instead of toy grids, the algorithms run on **actual road graphs** (10k–100k+ nodes), enabling a meaningful comparison of performance and behavior.

---

## What it does

- Loads real city graphs (OSMnx)
- Runs Dijkstra and A* on the **same graph, same start/goal**
- Measures:
  - path length (meters)
  - runtime
  - visited nodes (expansions)
  - edge relaxations (useful work)
- Visualizes explored roads and final paths side-by-side

---

## Architecture

- **Backend**: Python + Flask  
  - Graph cached in memory
  - Shared graph abstraction for both algorithms
- **Algorithms**:
  - Dijkstra
  - A* with admissible great-circle heuristic
- **Frontend**: JavaScript + Leaflet  
  - Synchronized maps
  - Animated exploration + metrics display

---

## Results (typical)

On large city graphs (e.g. Milan, London):
- A* expands **60–80% fewer nodes**
- Performs far fewer edge relaxations
- Runs significantly faster
- Returns the **same optimal path length** as Dijkstra

---

## Why this matters

This project demonstrates:
- Applying classic algorithms to messy real-world data
- Understanding *why* A* is faster, not just that it is
- Designing a clean, end-to-end system for fair comparison