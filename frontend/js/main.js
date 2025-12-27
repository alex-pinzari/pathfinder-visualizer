import { makeGrid, createGridUI, renderAll, clearVisitedAndPath } from "./map.js";
import { solveDijkstra } from "./api.js";
import { animateVisitedThenPath, getSpeedMs } from "./animation.js";

// ====== CONFIG ======
const ROWS = 25;
const COLS = 45;

// ====== DOM ======
const gridEl = document.getElementById("grid");
const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");
const modeBadge = document.getElementById("modeBadge");
const statusEl = document.getElementById("status");
const speedEl = document.getElementById("speed");

// ====== STATE ======
const state = {
  grid: makeGrid(ROWS, COLS),
  start: { r: Math.floor(ROWS / 2), c: Math.floor(COLS / 4) },
  goal:  { r: Math.floor(ROWS / 2), c: Math.floor(3 * COLS / 4) },
  mode: "WALL", // WALL | START | GOAL
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

// ====== GRID UI INIT ======
const { cellEls } = createGridUI({
  gridEl,
  rows: ROWS,
  cols: COLS,
  getState,
  setState,
  onStatus: status,
  onGridChanged: () => clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal }),
});

renderAll({ cellEls, grid: state.grid, start: state.start, goal: state.goal });

// ====== MODE ======
function setMode(m) {
  state.mode = m;
  modeBadge.textContent = m;
  status(`Mode: ${m}`);
}

// ====== BUTTONS ======
runBtn.addEventListener("click", run);
clearBtn.addEventListener("click", () => {
  if (state.isAnimating) return;
  state.grid = makeGrid(ROWS, COLS);
  clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
  renderAll({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
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
    run();
  }

  if (e.code === "KeyC") {
    if (state.isAnimating) return;
    clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });
    status("Cleared visited + path.");
  }
});

// ====== RUN ======
async function run() {
  if (state.isAnimating) return;

  clearVisitedAndPath({ cellEls, grid: state.grid, start: state.start, goal: state.goal });

  state.isAnimating = true;
  runBtn.disabled = true;
  clearBtn.disabled = true;
  status("Solving...");

  try {
    const { visited, path } = await solveDijkstra({
      grid: state.grid,
      start: state.start,
      goal: state.goal,
    });

    const delayMs = getSpeedMs(speedEl.value);

    status(`Animating... visited=${visited.length}, path=${path.length}`);

    await animateVisitedThenPath({
      visited,
      path,
      cellEls,
      start: state.start,
      goal: state.goal,
      delayMs,
    });

    status("Done.");
  } catch (err) {
    console.error(err);
    status(`Failed: ${err.message}`);
  } finally {
    state.isAnimating = false;
    runBtn.disabled = false;
    clearBtn.disabled = false;
  }
}
