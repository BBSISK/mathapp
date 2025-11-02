
// reports.js - lightweight reporting utilities using Chart.js
// Requires Chart.js v4+ via CDN on pages that use these charts.

async function fetchJSON(url) {
  const res = await fetch(url, { credentials: 'include' });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return await res.json();
}

// Heatmap renderer using a simple table + color mapping
export async function renderHeatmap(containerId, apiUrl) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const data = await fetchJSON(apiUrl);
  const { students, skills, mastery } = data; // mastery[studentId][skill] = percent 0..100

  // Build table
  const table = document.createElement('table');
  table.className = "min-w-full border-collapse";
  const thead = document.createElement('thead');
  const thr = document.createElement('tr');
  thr.innerHTML = `<th class="p-2 text-left sticky left-0 bg-white z-10">Student</th>` + 
                  skills.map(s => `<th class="p-2 text-xs">${s}</th>`).join('');
  thead.appendChild(thr);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');

  function colorFor(pct){
    if (pct === null || pct === undefined) return "#E5E7EB"; // not started
    if (pct < 40) return "#FCA5A5";
    if (pct < 60) return "#FCD34D";
    if (pct < 80) return "#86EFAC";
    return "#34D399";
  }

  students.forEach(stu => {
    const tr = document.createElement('tr');
    const nameCell = document.createElement('td');
    nameCell.className = "p-2 text-sm font-medium sticky left-0 bg-white z-10";
    nameCell.textContent = stu.name;
    tr.appendChild(nameCell);
    skills.forEach(skill => {
      const pct = (mastery[stu.id] && mastery[stu.id][skill] != null) ? mastery[stu.id][skill] : null;
      const td = document.createElement('td');
      td.className = "p-2 text-center text-xs border";
      td.style.backgroundColor = colorFor(pct);
      td.textContent = pct != null ? Math.round(pct) + "%" : "—";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.innerHTML = "";
  container.appendChild(table);
}

// Misconception tally: horizontal bar chart of counts per skill/tag
export async function renderMisconceptions(canvasId, apiUrl) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const data = await fetchJSON(apiUrl);
  const labels = data.labels;
  const counts = data.counts;
  if (!window.Chart) return;
  if (ctx._chart) { ctx._chart.destroy(); }
  ctx._chart = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Misconception Count', data: counts }] },
    options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
  });
}

// Calibration: scatter of confidence (x) vs accuracy (y)
export async function renderCalibration(canvasId, apiUrl) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const data = await fetchJSON(apiUrl);
  // data.points = [{student:"A", confidence:0.7, accuracy:0.62}, ...]
  if (!window.Chart) return;
  if (ctx._chart) { ctx._chart.destroy(); }
  ctx._chart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Students',
        data: data.points.map(p => ({x: Math.round(p.confidence*100), y: Math.round(p.accuracy*100)})),
        parsing: false
      }]
    },
    options: {
      scales: {
        x: { title: { text: 'Confidence (%)', display: true }, min: 0, max: 100 },
        y: { title: { text: 'Accuracy (%)', display: true }, min: 0, max: 100 }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(ctx){ const p=data.points[ctx.dataIndex]; return `${p.student}: ${ctx.parsed.x}% conf, ${ctx.parsed.y}% acc`; }
          }
        }
      }
    }
  });
}
