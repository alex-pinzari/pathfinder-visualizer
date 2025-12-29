let map = L.map("map").setView([45.4642, 9.1900], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const statusEl = document.getElementById("status");
const placeEl = document.getElementById("place");
const networkEl = document.getElementById("network");

let startMarker = null;
let goalMarker = null;
let dijkstraLine = null;
let astarLine = null;
let dijkstraVisited = null;
let astarVisited = null;

// ---- Visual styles ----
const PATH_STYLE_SOLID = {
  color: "#f1c40f",
  weight: 6,
  opacity: 1.0,
  lineCap: "round",
  lineJoin: "round",
};

const PATH_STYLE_DASHED = {
  ...PATH_STYLE_SOLID,
  weight: 5,
  dashArray: "8 8",
};

const EXPLORE_STYLE_SOLID = {
  color: "#0050ff",
  weight: 3,
  opacity: 0.7,
};

const EXPLORE_STYLE_DASHED = {
  ...EXPLORE_STYLE_SOLID,
  dashArray: "4 6",
};

function setStatus(msg) {
  statusEl.textContent = msg;
}

function clearOverlays() {
  if (dijkstraVisited) map.removeLayer(dijkstraVisited);
  if (astarVisited) map.removeLayer(astarVisited);
  if (dijkstraLine) map.removeLayer(dijkstraLine);
  if (astarLine) map.removeLayer(astarLine);
  dijkstraVisited = astarVisited = dijkstraLine = astarLine = null;
}

function clearAll() {
  if (startMarker) map.removeLayer(startMarker);
  if (goalMarker) map.removeLayer(goalMarker);
  startMarker = goalMarker = null;
  clearOverlays();
  setStatus("Click map: start, then goal.");
}

map.on("click", (e) => {
  const { lat, lng } = e.latlng;
  if (!startMarker) {
    startMarker = L.marker([lat, lng]).addTo(map).bindPopup("Start").openPopup();
    setStatus("Start set. Click to set goal.");
  } else if (!goalMarker) {
    goalMarker = L.marker([lat, lng]).addTo(map).bindPopup("Goal").openPopup();
    setStatus("Goal set. Press Compare.");
  } else {
    clearAll();
    startMarker = L.marker([lat, lng]).addTo(map).bindPopup("Start").openPopup();
  }
});

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function drawPath(pathLatLon, kind) {
  const latlngs = pathLatLon.map(p => [p[0], p[1]]);
  const style = kind === "dijkstra" ? PATH_STYLE_SOLID : PATH_STYLE_DASHED;
  return L.polyline(latlngs, style).addTo(map);
}

function animateVisited(latlonList, kind, onDone) {
  const latlngs = latlonList.map(p => [p[0], p[1]]);
  const style = kind === "dijkstra" ? EXPLORE_STYLE_SOLID : EXPLORE_STYLE_DASHED;
  const line = L.polyline([], style).addTo(map);

  let i = 0;
  const batch = 250;

  function step() {
    const end = Math.min(i + batch, latlngs.length);
    for (; i < end; i++) line.addLatLng(latlngs[i]);
    if (i < latlngs.length) requestAnimationFrame(step);
    else onDone?.(line);
  }
  step();
}

document.getElementById("compareBtn").addEventListener("click", async () => {
  if (!startMarker || !goalMarker) return setStatus("Set start and goal first.");
  clearOverlays();

  const s = startMarker.getLatLng();
  const g = goalMarker.getLatLng();

  const payload = {
    place: placeEl.value.trim(),
    network: networkEl.value,
    start: [s.lat, s.lng],
    goal: [g.lat, g.lng],
  };


  setStatus("Routing...");
  const data = await postJSON("/osm/route/compare", payload);

  animateVisited(data.dijkstra.visited, "dijkstra", (dl) => {
    dijkstraVisited = dl;
    animateVisited(data.astar.visited, "astar", (al) => {
      astarVisited = al;
      dijkstraLine = drawPath(data.dijkstra.path, "dijkstra");
      astarLine = drawPath(data.astar.path, "astar");
      dijkstraLine.bringToFront();
      astarLine.bringToFront();
      map.fitBounds(dijkstraLine.getBounds(), { padding: [20, 20] });
      setStatus("Done.");
    });
  });
});

document.getElementById("clearBtn").addEventListener("click", clearAll);