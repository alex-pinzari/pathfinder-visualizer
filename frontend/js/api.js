const API_BASE = ""; // same-origin. If Flask is separate: "http://localhost:5000"

export async function solveDijkstra({ grid, start, goal }) {
  const res = await fetch(`${API_BASE}/solve/dijkstra`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grid,
      start: [start.r, start.c],
      goal: [goal.r, goal.c],
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Backend error ${res.status}: ${text || res.statusText}`);
  }

  const data = await res.json();
  return {
    visited: data.visited ?? [],
    path: data.path ?? [],
  };
}

