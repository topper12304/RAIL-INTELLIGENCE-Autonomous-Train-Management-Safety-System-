const BASE = "http://127.0.0.1:8000";

function showResult(outputId, data, title) {
  const el = document.getElementById(outputId);
  if (data.error) {
    el.innerHTML = `<div class="error">❌ ${data.error}</div>`;
  } else {
    el.innerHTML = `<h4>${title}</h4><pre>${JSON.stringify(data, null, 2)}</pre>`;
  }
}

function showSimpleResult(outputId, html) {
  document.getElementById(outputId).innerHTML = `<div class="result">${html}</div>`;
}

async function computePath() {
  try {
    const text = document.getElementById("networkInput").value.trim();
    if (!text) throw new Error("Enter network JSON");
    const data = JSON.parse(text);
    console.log("Network data:", data);
    console.log("Fetching", `${BASE}/network/shortest-path`);
    const res = await fetch(`${BASE}/network/shortest-path`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    console.log("Response status:", res.status);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    const result = await res.json();
    showResult("networkOutput", result, "✅ Shortest Path Found");
  } catch (e) {
    console.error("Network error:", e);
    showResult("networkOutput", {error: e.message}, "Network Error");
  }
}

function loadNetworkExample() {
  document.getElementById("networkInput").value = `{
  "nodes": ["A", "B", "C"],
  "edges": [{"u":"A","v":"B","w":1},{"u":"B","v":"C","w":2},{"u":"A","v":"C","w":5}],
  "source": "A",
  "target": "C"
}`;
}

async function computePlatforms() {
  try {
    const inputs = document.querySelectorAll('#platformIntervals .time-input');
    const intervals = [];
    for (let i = 0; i < inputs.length; i += 2) {
      const arrStr = inputs[i].value.trim();
      const depStr = inputs[i+1].value.trim();
      if (arrStr && depStr) {
        const arr = parseInt(arrStr);
        const dep = parseInt(depStr);
        if (!isNaN(arr) && !isNaN(dep) && arr < dep) {
          intervals.push({arrival: arr, departure: dep});
        }
      }
    }
    if (intervals.length === 0) throw new Error("Add at least one train interval");
    const data = {intervals};
    console.log("Platform data:", data);
    const res = await fetch(`${BASE}/platform/min-platforms`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    showSimpleResult("platformOutput", `<strong>🚉 Min Platforms:</strong> <span style="font-size:1.5em;color:#4CAF50">${result.min_platforms}</span>`);
  } catch (e) {
    console.error("Platform error:", e);
    showResult("platformOutput", {error: e.message}, "Platform Error");
  }
}

function addInterval() {
  const container = document.getElementById("platformIntervals");
  const row = document.createElement("div");
  row.className = "interval-row";
  row.innerHTML = `
    <input type="number" placeholder="Arrival (min)" class="time-input" min="0">
    <input type="number" placeholder="Departure (min)" class="time-input" min="0">
    <button type="button" onclick="removeInterval(this)">❌</button>
  `;
  container.appendChild(row);
  row.querySelector('.time-input').focus();
}

function removeInterval(btn) {
  if (document.querySelectorAll('#platformIntervals .interval-row').length > 1) {
    btn.parentElement.remove();
  }
}

function loadPlatformExample() {
  document.getElementById("platformIntervals").innerHTML = '';
  const examples = [[900,910],[940,1200],[950,1120],[1100,1130],[1500,1900],[1800,2000]];
  examples.forEach(([arr, dep]) => addIntervalCustom(arr, dep));
}

function addIntervalCustom(arr, dep) {
  addInterval();
  const inputs = document.querySelectorAll('#platformIntervals .time-input');
  const lastArr = inputs[inputs.length - 2];
  const lastDep = inputs[inputs.length - 1];
  lastArr.value = arr;
  lastDep.value = dep;
}

async function detectFault() {
  try {
    const coachStr = document.getElementById("coachIds").value.trim();
    if (!coachStr) throw new Error("Enter coach IDs");
    const coachIds = coachStr.split(',').map(s => s.trim()).filter(Boolean);
    const faultyIndex = parseInt(document.getElementById("faultyIndex").value);
    if (isNaN(faultyIndex)) throw new Error("Valid faulty index");
    const data = {coach_ids: coachIds, faulty_index: faultyIndex};
    console.log("Coach data:", data);
    const res = await fetch(`${BASE}/coach/fault-location`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    let msg = `Coach sequence: ${result.coach_ids.join(' → ')}`;
    if (result.faulty_index === -1) {
      msg += '<br><strong style="color:green">✅ No faulty coach detected</strong>';
    } else {
      msg += `<br><strong style="color:orange">⚠️ Fault at index ${result.faulty_index}: ${result.coach_ids[result.faulty_index]}</strong>`;
    }
    showSimpleResult("coachOutput", msg);
  } catch (e) {
    console.error("Coach error:", e);
    showResult("coachOutput", {error: e.message}, "Coach Error");
  }
}

function loadCoachExample() {
  document.getElementById("coachIds").value = "C1, C2, C3, C4";
  document.getElementById("faultyIndex").value = 1;
}

function addZone() {
  const container = document.getElementById("unsafeZones");
  const row = document.createElement("div");
  row.className = "zone-row";
  row.innerHTML = `
    <input type="number" placeholder="Start km" class="zone-input" min="0">
    <input type="number" placeholder="End km" class="zone-input" min="0">
    <button type="button" onclick="removeZone(this)">❌</button>
  `;
  container.appendChild(row);
  row.querySelector('.zone-input').focus();
}

function removeZone(btn) {
  if (document.querySelectorAll('#unsafeZones .zone-row').length > 1) {
    btn.parentElement.remove();
  }
}

async function safetyStop() {
  try {
    const positionStr = document.getElementById("safetyPosition").value.trim();
    if (!positionStr) throw new Error("Enter position");
    const position = parseInt(positionStr);
    const inputs = document.querySelectorAll('#unsafeZones .zone-input');
    const zones = [];
    for (let i = 0; i < inputs.length; i += 2) {
      const startStr = inputs[i].value.trim();
      const endStr = inputs[i+1].value.trim();
      if (startStr && endStr) {
        const start = parseInt(startStr);
        const end = parseInt(endStr);
        if (!isNaN(start) && !isNaN(end) && start < end) {
          zones.push({start, end});
        }
      }
    }
    const data = {position, unsafe_zones: zones};
    console.log("Safety data:", data);
    const res = await fetch(`${BASE}/safety/emergency-stop`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    const result = await res.json();
    const statusEmoji = result.final_state === "STOPPED" ? "🛑" : "⚠️";
    let msg = `<strong>${statusEmoji} State: ${result.final_state}</strong><br>`;
    if (result.final_position !== position) {
      msg += `<strong style="color:orange">Moved to safe: ${result.final_position} km (from ${position} km)</strong>`;
    } else {
      msg += `Position: ${result.final_position} km`;
    }
    showSimpleResult("safetyOutput", msg);
  } catch (e) {
    console.error("Safety error:", e);
    showResult("safetyOutput", {error: e.message}, "Safety Error");
  }
}

function loadSafetyExample() {
  document.getElementById("safetyPosition").value = "15";
  document.getElementById("unsafeZones").innerHTML = '';
  addZoneCustom(10, 20);
}

function addZoneCustom(start, end) {
  addZone();
  const inputs = document.querySelectorAll('#unsafeZones .zone-input');
  const lastStart = inputs[inputs.length - 2];
  const lastEnd = inputs[inputs.length - 1];
  lastStart.value = start;
  lastEnd.value = end;
}

// Auto-load examples on start
window.onload = () => {
  loadNetworkExample();
  loadCoachExample();
  loadSafetyExample();
  addInterval(); // one empty for platforms
};
