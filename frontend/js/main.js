import {
  makeGrid,
  createGridUI,
  createGridDisplay,
  renderAll,
  clearVisitedAndPath,
} from "./map.js";

import { solveDijkstra, solveAstar, solveCompare } from "./api.js";
import { animateVisitedThenPath, getSpeedMs } from "./animation.js";

// ====== CONFIG ======
const ROWS = 25;
const COLS = 45;

// ====== DOM ======
const gridEl = document.getElementById("grid");
const gridDijkstraEl = document.getElementById("gridDijkstra");
const gridAstarEl = document.getElementById("gridAstar");

const runBtn = document.getElementById("runBtn");
const runAstarBtn = document.getElementById("runAstarBtn");
const compareBtn = document.getElementById("compareBtn");
const clearBtn = document.getElementById("clearBtn");

const modeBadge = document.getElementById("modeBadge");
const statusEl = document.getElementById("status");
const speedEl = document.getElementById("speed");

// ====== STATE ======
const state = {
  grid: makeGrid(ROWS, COLS),
  start: { r: Math.floor(ROWS / 2), c: Math.floor(COLS / 4) },
  goal: { r: Math.floor(ROWS / 2), c: Math.floor((3 * COLS) / 4) },
  mode: "WALL",
  isAnimating: false,
};

function getState() {
  return state;
}

function setState(partial) {
  Object.assign(state, partial);
}

function status(msg) {
  statusEl.textContent = msg;
}

// ====== EDITOR GRID INIT ======
const { cellEls } = createGridUI({
  gridEl,
  rows: ROWS,
  cols: COLS,
  getState,
  setState,
  onStatus: status,
  onGridChanged: () => {
    // clear overlays everywhere when the editor changes
    clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
    syncResultGrids();
    clearResultsOnly();
  },
});

// ====== RESULT GRIDS INIT (read-only) ======
let cellElsDijkstra = null;
let cellElsAstar = null;

if (gridDijkstraEl) {
  cellElsDijkstra = createGridDisplay({ gridEl: gridDijkstraEl, rows: ROWS, cols: COLS }).cellEls;
}
if (gridAstarEl) {
  cellElsAstar = createGridDisplay({ gridEl: gridAstarEl, rows: ROWS, cols: COLS }).cellEls;
}

// Initial render (editor always)
renderAll({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
// Sync results if they exist
syncResultGrids();

// ====== MODE ======
function setMode(m) {
  state.mode = m;
  modeBadge.textContent = m;
  status(`Mode: ${m}`);
}

// ====== HELPERS ======
function clearResultsOnly() {
  if (cellElsDijkstra) {
    clearVisitedAndPath({ cellEls: cellElsDijkstra, grid: state.grid, start: state.start, goal: state.goal });
  }
  if (cellElsAstar) {
    clearVisitedAndPath({ cellEls: cellElsAstar, grid: state.grid, start: state.start, goal: state.goal });
  }
}

function syncResultGrids() {
  if (!state.grid) return; // paranoia guard

  if (cellElsDijkstra) {
    renderAll({ cellEls: cellElsDijkstra, grid: state.grid, start: state.start, goal: state.goal });
  }
  if (cellElsAstar) {
    renderAll({ cellEls: cellElsAstar, grid: state.grid, start: state.start, goal: state.goal });
  }
}

// ====== BUTTONS ======
runBtn.addEventListener("click", () => runSingle("dijkstra"));
runAstarBtn.addEventListener("click", () => runSingle("astar"));
compareBtn.addEventListener("click", runCompare);

clearBtn.addEventListener("click", () => {
  if (state.isAnimating) return;

  state.grid = makeGrid(ROWS, COLS);

  renderAll({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
  clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });

  syncResultGrids();
  clearResultsOnly();

  status("Cleared walls + visited + path.");
});

// ====== KEYBOARD ======
document.addEventListener("keydown", (e) => {
  if (e.repeat) return;

  if (e.code === "KeyW") setMode("WALL");
  if (e.code === "KeyS") setMode("START");
  if (e.code === "KeyG") setMode("GOAL");

  if (e.code === "Space") {
    e.preventDefault();
    runSingle("dijkstra");
  }

  if (e.code === "KeyC") {
    if (state.isAnimating) return;

    clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
    clearResultsOnly();
    status("Cleared visited + path.");
  }
});

// ====== RUN SINGLE ======
async function runSingle(algo) {
  if (state.isAnimating) return;

  syncResultGrids();
  clearResultsOnly();

  state.isAnimating = true;
  runBtn.disabled = true;
  runAstarBtn.disabled = true;
  compareBtn.disabled = true;
  clearBtn.disabled = true;

  const algoName = algo === "astar" ? "A*" : "Dijkstra";
  status(`Solving with ${algoName}...`);

  try {
    const solver = algo === "astar" ? solveAstar : solveDijkstra;
    const { visited, path, found, metrics } = await solver({
      grid: state.grid,
      start: state.start,
      goal: state.goal,
    });

    const delayMs = getSpeedMs(speedEl.value);
    const target = algo === "astar" ? cellElsAstar : cellElsDijkstra;

    if (!target) {
      status(`No panel found for ${algoName}. Check grid IDs in index.html.`);
      return;
    }

    if (metrics) {
      status(`${algoName}: visited=${metrics.visited_count}, steps=${metrics.path_length}, ${metrics.runtime_ms.toFixed(2)}ms`);
    }

    await animateVisitedThenPath({
      visited,
      path,
      cellEls: target,
      start: state.start,
      goal: state.goal,
      delayMs,
    });

    status(found ? `${algoName}: Done.` : `${algoName}: No path found.`);
  } catch (err) {
    console.error(err);
    status(`Failed: ${err.message}`);
  } finally {
    state.isAnimating = false;
    runBtn.disabled = false;
    runAstarBtn.disabled = false;
    compareBtn.disabled = false;
    clearBtn.disabled = false;
  }
}

// ====== RUN COMPARE ======
async function runCompare() {
  if (state.isAnimating) return;

  syncResultGrids();
  clearResultsOnly();

  state.isAnimating = true;
  runBtn.disabled = true;
  runAstarBtn.disabled = true;
  compareBtn.disabled = true;
  clearBtn.disabled = true;

  status("Comparing Dijkstra vs A*...");

  try {
    if (!cellElsDijkstra || !cellElsAstar) {
      status("Missing result panels. Check grid IDs in index.html.");
      return;
    }

    const { dijkstra, astar } = await solveCompare({
      grid: state.grid,
      start: state.start,
      goal: state.goal,
    });

    const delayMs = getSpeedMs(speedEl.value);

    const dj = dijkstra.metrics
      ? `D: v=${dijkstra.metrics.visited_count}, steps=${dijkstra.metrics.path_length}, ${dijkstra.metrics.runtime_ms.toFixed(2)}ms`
      : `D: v=${(dijkstra.visited ?? []).length}`;

    const as = astar.metrics
      ? `A*: v=${astar.metrics.visited_count}, steps=${astar.metrics.path_length}, ${astar.metrics.runtime_ms.toFixed(2)}ms`
      : `A*: v=${(astar.visited ?? []).length}`;

    status(`${dj} | ${as}`);

    await Promise.all([
      animateVisitedThenPath({
        visited: dijkstra.visited ?? [],
        path: dijkstra.path ?? [],
        cellEls: cellElsDijkstra,
        start: state.start,
        goal: state.goal,
        delayMs,
      }),
      animateVisitedThenPath({
        visited: astar.visited ?? [],
        path: astar.path ?? [],
        cellEls: cellElsAstar,
        start: state.start,
        goal: state.goal,
        delayMs,
      }),
    ]);

    status("Compare: Done.");
  } catch (err) {
    console.error(err);
    status(`Failed: ${err.message}`);
  } finally {
    state.isAnimating = false;
    runBtn.disabled = false;
    runAstarBtn.disabled = false;
    compareBtn.disabled = false;
    clearBtn.disabled = false;
  }
}