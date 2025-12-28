export function makeGrid(rows, cols) {
  return Array.from({ length: rows }, () => Array(cols).fill(0));
}

function sameCell(a, b) {
  return a.r === b.r && a.c === b.c;
}

export function createGridUI({
  gridEl,
  rows,
  cols,
  getState,      // () => { grid, start, goal, mode, isAnimating }
  setState,      // (partial) => void
  onStatus,      // (msg) => void
  onGridChanged, // () => void (e.g., clear visited/path)
}) {
  gridEl.style.gridTemplateColumns = `repeat(${cols}, var(--cell))`;

  const cellEls = Array.from({ length: rows }, () => Array(cols).fill(null));
  gridEl.innerHTML = "";

  let mouseDown = false;
  let paintWallValue = 1;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.r = String(r);
      cell.dataset.c = String(c);

      cell.addEventListener("mousedown", () => {
        const st = getState();
        if (st.isAnimating) return;

        mouseDown = true;

        if (st.mode === "START") {
          if (!sameCell({ r, c }, st.goal)) {
            st.grid[r][c] = 0;
            setState({ start: { r, c } });
            onGridChanged();
            renderAll({ cellEls, grid: st.grid, start: { r, c }, goal: st.goal });
            onStatus(`Start set to (${r}, ${c}).`);
          }
          return;
        }

        if (st.mode === "GOAL") {
          if (!sameCell({ r, c }, st.start)) {
            st.grid[r][c] = 0;
            setState({ goal: { r, c } });
            onGridChanged();
            renderAll({ cellEls, grid: st.grid, start: st.start, goal: { r, c } });
            onStatus(`Goal set to (${r}, ${c}).`);
          }
          return;
        }

        // WALL mode
        if (sameCell({ r, c }, st.start) || sameCell({ r, c }, st.goal)) return;

        const currentlyWall = st.grid[r][c] === 1;
        paintWallValue = currentlyWall ? 0 : 1;
        st.grid[r][c] = paintWallValue;

        // IMPORTANT: clear result overlays when walls change
        onGridChanged();

        renderCell({ el: cellEls[r][c], r, c, grid: st.grid, start: st.start, goal: st.goal });
      });

      cell.addEventListener("mouseenter", () => {
        const st = getState();
        if (st.isAnimating) return;
        if (!mouseDown) return;
        if (st.mode !== "WALL") return;

        if (sameCell({ r, c }, st.start) || sameCell({ r, c }, st.goal)) return;

        st.grid[r][c] = paintWallValue;

        // IMPORTANT: clear result overlays when walls change
        onGridChanged();

        renderCell({ el: cellEls[r][c], r, c, grid: st.grid, start: st.start, goal: st.goal });
      });

      gridEl.appendChild(cell);
      cellEls[r][c] = cell;
    }
  }

  window.addEventListener("mouseup", () => {
    mouseDown = false;
  });

  return { cellEls };
}

/**
 * Read-only grid (no mouse handlers) for Dijkstra/A* panels.
 */
export function createGridDisplay({ gridEl, rows, cols }) {
  gridEl.style.gridTemplateColumns = `repeat(${cols}, var(--cell))`;

  const cellEls = Array.from({ length: rows }, () => Array(cols).fill(null));
  gridEl.innerHTML = "";

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.r = String(r);
      cell.dataset.c = String(c);
      gridEl.appendChild(cell);
      cellEls[r][c] = cell;
    }
  }

  return { cellEls };
}

export function renderAll({ cellEls, grid, start, goal }) {
  for (let r = 0; r < cellEls.length; r++) {
    for (let c = 0; c < cellEls[0].length; c++) {
      renderCell({ el: cellEls[r][c], r, c, grid, start, goal });
    }
  }
}

export function renderCell({ el, r, c, grid, start, goal }) {
  el.classList.remove("wall", "start", "goal");

  if (grid[r][c] === 1) el.classList.add("wall");
  if (r === start.r && c === start.c) el.classList.add("start");
  if (r === goal.r && c === goal.c) el.classList.add("goal");
}

export function clearVisitedAndPath({ cellEls, grid, start, goal }) {
  for (let r = 0; r < cellEls.length; r++) {
    for (let c = 0; c < cellEls[0].length; c++) {
      const el = cellEls[r][c];
      el.classList.remove("visited", "path");
      renderCell({ el, r, c, grid, start, goal });
    }
  }
}