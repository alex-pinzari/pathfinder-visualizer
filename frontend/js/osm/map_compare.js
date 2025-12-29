const statusEl = document.getElementById("metrics");
const placeEl = document.getElementById("place");
const showVisitedEl = document.getElementById("showVisited");
const speedEl = document.getElementById("speed");

// ---- Visual styles ----
const PATH_STYLE = {
  color: "#f1c40f", // yellow
  weight: 6,
  opacity: 1.0,
  lineCap: "round",
  lineJoin: "round",
};

const EXPLORE_STYLE_SOLID = {
  color: "#0050ff", // strong blue
  weight: 3,
  opacity: 0.7,
  lineCap: "round",
};

const EXPLORE_STYLE_DASHED = {
  ...EXPLORE_STYLE_SOLID,
  dashArray: "4 6",
};

function setStatus(msg) {
  statusEl.textContent = msg;
}

function makeMap(divId) {
  const m = L.map(divId, { zoomControl: false }).setView([45.4642, 9.1900], 12);
  L.control.zoom({ position: "bottomright" }).addTo(m);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(m);

  return m;
}

const mapLeft = makeMap("mapLeft");
const mapRight = makeMap("mapRight");

// --- sync pan/zoom ---
let syncing = false;
function syncMaps(from, to) {
  if (syncing) return;
  syncing = true;
  to.setView(from.getCenter(), from.getZoom(), { animate: false });
  syncing = false;
}
mapLeft.on("move", () => syncMaps(mapLeft, mapRight));
mapRight.on("move", () => syncMaps(mapRight, mapLeft));

// --- markers & layers ---
let startMarkerL = null, goalMarkerL = null;
let startMarkerR = null, goalMarkerR = null;
let exploredLayerL = null, pathLineL = null;
let exploredLayerR = null, pathLineR = null;

function clearOverlays() {
  if (exploredLayerL) mapLeft.removeLayer(exploredLayerL);
  if (pathLineL) mapLeft.removeLayer(pathLineL);
  if (exploredLayerR) mapRight.removeLayer(exploredLayerR);
  if (pathLineR) mapRight.removeLayer(pathLineR);
  exploredLayerL = exploredLayerR = pathLineL = pathLineR = null;
}

function clearAll() {
  if (startMarkerL) mapLeft.removeLayer(startMarkerL);
  if (goalMarkerL) mapLeft.removeLayer(goalMarkerL);
  if (startMarkerR) mapRight.removeLayer(startMarkerR);
  if (goalMarkerR) mapRight.removeLayer(goalMarkerR);
  startMarkerL = goalMarkerL = startMarkerR = goalMarkerR = null;
  clearOverlays();
  setStatus("Click either map: start, then goal.");
}

function setStart(lat, lon) {
  clearAll();
  startMarkerL = L.marker([lat, lon]).addTo(mapLeft).bindPopup("Start");
  startMarkerR = L.marker([lat, lon]).addTo(mapRight).bindPopup("Start");
  setStatus("Start set. Click to set goal.");
}

function setGoal(lat, lon) {
  goalMarkerL = L.marker([lat, lon]).addTo(mapLeft).bindPopup("Goal");
  goalMarkerR = L.marker([lat, lon]).addTo(mapRight).bindPopup("Goal");
  setStatus("Goal set. Press Compare.");
}

function handleMapClick(e) {
  const { lat, lng } = e.latlng;
  if (!startMarkerL) return setStart(lat, lng);
  if (!goalMarkerL) return setGoal(lat, lng);
  setStart(lat, lng);
}

mapLeft.on("click", handleMapClick);
mapRight.on("click", handleMapClick);

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function drawPath(map, pathLatLon) {
  const latlngs = (pathLatLon || []).map(p => [p[0], p[1]]);
  return L.polyline(latlngs, PATH_STYLE).addTo(map);
}

function animateExploredEdges(map, segments, dashed, onDone) {
  const segs = segments || [];
  const group = L.layerGroup().addTo(map);
  const style = EXPLORE_STYLE_SOLID;
  let i = 0;
  const batch = parseInt(speedEl?.value || "1200", 10);

  function step() {
    const end = Math.min(i + batch, segs.length);
    for (; i < end; i++) {
      L.polyline(segs[i], style).addTo(group);
    }
    if (i < segs.length) requestAnimationFrame(step);
    else onDone?.(group);
  }
  step();
}

document.getElementById("compareBtn").addEventListener("click", async () => {
  if (!startMarkerL || !goalMarkerL) return setStatus("Set start and goal first.");
  clearOverlays();

  const s = startMarkerL.getLatLng();
  const g = goalMarkerL.getLatLng();

  const payload = {
    place: placeEl.value.trim(),
    network: "drive",
    start: [s.lat, s.lng],
    goal: [g.lat, g.lng],
  };


  setStatus("Routing...");
  const data = await postJSON("/osm/route/compare", payload);

  const d = data.dijkstra;
  const a = data.astar;

  if (showVisitedEl.checked) {
    animateExploredEdges(mapLeft, d.explored_edges, false, (l) => {
      exploredLayerL = l;
      animateExploredEdges(mapRight, a.explored_edges, true, (r) => {
        exploredLayerR = r;
        pathLineL = drawPath(mapLeft, d.path);
        pathLineR = drawPath(mapRight, a.path);
        pathLineL.bringToFront();
        pathLineR.bringToFront();
      });
    });
  } else {
    pathLineL = drawPath(mapLeft, d.path);
    pathLineR = drawPath(mapRight, a.path);
    pathLineL.bringToFront();
    pathLineR.bringToFront();
  }

  setStatus(
    `Dijkstra: ${d.distance_m.toFixed(0)}m, ${d.runtime_ms.toFixed(1)}ms | ` +
    `A*: ${a.distance_m.toFixed(0)}m, ${a.runtime_ms.toFixed(1)}ms`
  );
});

document.getElementById("clearBtn").addEventListener("click", clearAll);