function sameCellRC(r, c, p) {
  return r === p.r && c === p.c;
}

export function getSpeedMs(speedSliderValue) {
  // slider 1..200; higher = faster. Map ~200ms..1ms
  const v = Number(speedSliderValue);
  return Math.max(1, Math.floor(200 / v));
}

export function animateVisitedThenPath({
  visited,
  path,
  cellEls,
  start,
  goal,
  delayMs,
}) {
  return new Promise((resolve) => {
    let i = 0;

    const stepVisited = () => {
      const batch = 10; // paint multiple per tick
      for (let k = 0; k < batch && i < visited.length; k++, i++) {
        const [r, c] = visited[i];
        if (sameCellRC(r, c, start) || sameCellRC(r, c, goal)) continue;
        cellEls[r][c].classList.add("visited");
      }

      if (i < visited.length) {
        setTimeout(stepVisited, delayMs);
      } else {
        animatePath({ path, cellEls, start, goal, delayMs }).then(resolve);
      }
    };

    stepVisited();
  });
}

function animatePath({ path, cellEls, start, goal, delayMs }) {
  return new Promise((resolve) => {
    let i = 0;

    const stepPath = () => {
      const pair = path[i];
      if (pair) {
        const [r, c] = pair;
        if (!sameCellRC(r, c, start) && !sameCellRC(r, c, goal)) {
          cellEls[r][c].classList.add("path");
        }
      }

      i++;
      if (i < path.length) setTimeout(stepPath, delayMs);
      else resolve();
    };

    stepPath();
  });
}
