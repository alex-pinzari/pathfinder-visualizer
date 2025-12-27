from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import traceback
from pathfinding.grid import Grid
from pathfinding.dijkstra import dijkstra

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/solve/dijkstra")
def solve_dijkstra():
    try:
        data = request.get_json(force=True)

        cells = data.get("grid")
        start = data.get("start")
        goal = data.get("goal")

        # basic validation (keep it; saves you time)
        if not isinstance(cells, list) or not cells or not all(isinstance(row, list) for row in cells):
            return jsonify({"error": "grid must be a 2D list"}), 400
        if not (isinstance(start, list) and len(start) == 2 and all(isinstance(x, int) for x in start)):
            return jsonify({"error": "start must be [row,col] ints"}), 400
        if not (isinstance(goal, list) and len(goal) == 2 and all(isinstance(x, int) for x in goal)):
            return jsonify({"error": "goal must be [row,col] ints"}), 400

        # now safe to print
        print("HIT /solve/dijkstra", flush=True)
        print("start", start, "goal", goal, flush=True)
        print("grid size", len(cells), len(cells[0]), flush=True)

        grid = Grid(cells)
        s = (start[0], start[1])
        g = (goal[0], goal[1])

        # bounds + walls checks
        if not grid.in_bounds(s) or not grid.in_bounds(g):
            return jsonify({"error": "start/goal out of bounds"}), 400
        if not grid.is_walkable(s) or not grid.is_walkable(g):
            return jsonify({"error": "start/goal must be on walkable cells (0)"}), 400

        path, visited = dijkstra(grid, s, g)

        return jsonify({
            "path": [[r, c] for (r, c) in path],
            "visited": [[r, c] for (r, c) in visited],
            "found": len(path) > 0
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(tb, flush=True)
        return jsonify({"error": str(e), "traceback": tb}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
