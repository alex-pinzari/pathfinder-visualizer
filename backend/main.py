from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import traceback
import time

from pathfinding.grid.grid import Grid
from pathfinding.grid.dijkstra import dijkstra
from pathfinding.grid.astar import astar

from pathfinding.osm.graph_cache import get_graph
from pathfinding.osm.routing import route_compare_own

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


# ---------------------------
# GRID ENDPOINTS (existing)
# ---------------------------

@app.post("/solve/dijkstra")
def solve_dijkstra():
    try:
        data = request.get_json(force=True)

        cells = data.get("grid")
        start = data.get("start")
        goal = data.get("goal")

        if not isinstance(cells, list) or not cells or not all(isinstance(row, list) for row in cells):
            return jsonify({"error": "grid must be a 2D list"}), 400
        if not (isinstance(start, list) and len(start) == 2 and all(isinstance(x, int) for x in start)):
            return jsonify({"error": "start must be [row,col] ints"}), 400
        if not (isinstance(goal, list) and len(goal) == 2 and all(isinstance(x, int) for x in goal)):
            return jsonify({"error": "goal must be [row,col] ints"}), 400

        grid = Grid(cells)
        s = (start[0], start[1])
        g = (goal[0], goal[1])

        if not grid.in_bounds(s) or not grid.in_bounds(g):
            return jsonify({"error": "start/goal out of bounds"}), 400
        if not grid.is_walkable(s) or not grid.is_walkable(g):
            return jsonify({"error": "start/goal must be on walkable cells (0)"}), 400

        t0 = time.perf_counter()
        path, visited = dijkstra(grid, s, g)
        ms = (time.perf_counter() - t0) * 1000.0

        return jsonify({
            "path": [[r, c] for (r, c) in path],
            "visited": [[r, c] for (r, c) in visited],
            "found": len(path) > 0,
            "metrics": {
                "visited_count": len(visited),
                "path_length": max(0, len(path) - 1),
                "runtime_ms": ms,
            }
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(tb, flush=True)
        return jsonify({"error": str(e), "traceback": tb}), 500


@app.post("/solve/astar")
def solve_astar():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Expected JSON body"}), 400

        cells = data.get("grid")
        start = data.get("start")
        goal = data.get("goal")

        if not isinstance(cells, list) or not cells or not all(isinstance(row, list) for row in cells):
            return jsonify({"error": "grid must be a 2D list"}), 400
        if not (isinstance(start, list) and len(start) == 2 and all(isinstance(x, int) for x in start)):
            return jsonify({"error": "start must be [row,col] ints"}), 400
        if not (isinstance(goal, list) and len(goal) == 2 and all(isinstance(x, int) for x in goal)):
            return jsonify({"error": "goal must be [row,col] ints"}), 400

        grid = Grid(cells)
        s = (start[0], start[1])
        g = (goal[0], goal[1])

        if not grid.in_bounds(s) or not grid.in_bounds(g):
            return jsonify({"error": "start/goal out of bounds"}), 400
        if not grid.is_walkable(s) or not grid.is_walkable(g):
            return jsonify({"error": "start/goal must be on walkable cells (0)"}), 400

        t0 = time.perf_counter()
        visited, path, found = astar(grid, s, g)
        ms = (time.perf_counter() - t0) * 1000.0

        return jsonify({
            "visited": [[r, c] for (r, c) in visited],
            "path": [[r, c] for (r, c) in path],
            "found": found,
            "metrics": {
                "visited_count": len(visited),
                "path_length": max(0, len(path) - 1),
                "runtime_ms": ms,
            }
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(tb, flush=True)
        return jsonify({"error": str(e), "traceback": tb}), 500


@app.post("/solve/compare")
def solve_compare():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Expected JSON body"}), 400

        cells = data.get("grid")
        start = data.get("start")
        goal = data.get("goal")

        if not isinstance(cells, list) or not cells or not all(isinstance(row, list) for row in cells):
            return jsonify({"error": "grid must be a 2D list"}), 400
        if not (isinstance(start, list) and len(start) == 2 and all(isinstance(x, int) for x in start)):
            return jsonify({"error": "start must be [row,col] ints"}), 400
        if not (isinstance(goal, list) and len(goal) == 2 and all(isinstance(x, int) for x in goal)):
            return jsonify({"error": "goal must be [row,col] ints"}), 400

        grid = Grid(cells)
        s = (start[0], start[1])
        g = (goal[0], goal[1])

        if not grid.in_bounds(s) or not grid.in_bounds(g):
            return jsonify({"error": "start/goal out of bounds"}), 400
        if not grid.is_walkable(s) or not grid.is_walkable(g):
            return jsonify({"error": "start/goal must be on walkable cells (0)"}), 400

        t0 = time.perf_counter()
        dj_path, dj_visited = dijkstra(grid, s, g)
        dj_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        a_visited, a_path, a_found = astar(grid, s, g)
        a_ms = (time.perf_counter() - t1) * 1000.0

        return jsonify({
            "dijkstra": {
                "visited": [[r, c] for (r, c) in dj_visited],
                "path": [[r, c] for (r, c) in dj_path],
                "found": len(dj_path) > 0,
                "metrics": {
                    "visited_count": len(dj_visited),
                    "path_length": max(0, len(dj_path) - 1),
                    "runtime_ms": dj_ms,
                },
            },
            "astar": {
                "visited": [[r, c] for (r, c) in a_visited],
                "path": [[r, c] for (r, c) in a_path],
                "found": a_found,
                "metrics": {
                    "visited_count": len(a_visited),
                    "path_length": max(0, len(a_path) - 1),
                    "runtime_ms": a_ms,
                },
            }
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(tb, flush=True)
        return jsonify({"error": str(e), "traceback": tb}), 500


@app.post("/osm/route/compare")
def osm_route_compare():
    data = request.get_json(silent=True) or {}
    place = data.get("place", "Delft, Netherlands")
    network = data.get("network", "drive")

    start = data.get("start")  # [lat, lon]
    goal = data.get("goal")    # [lat, lon]
    if not (isinstance(start, list) and len(start) == 2 and isinstance(goal, list) and len(goal) == 2):
        return jsonify({"error": "Expected start and goal as [lat, lon]"}), 400

    G = get_graph(place, network)

    # ✅ THIS is the important part: use YOUR compare function (path + visited + metrics)
    res = route_compare_own(G, start[0], start[1], goal[0], goal[1])
    res["meta"] = {"place": place, "network": network}

    return jsonify(res)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)