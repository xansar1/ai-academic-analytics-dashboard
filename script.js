const API = "https://ai-academic-backend.onrender.com/api";

// =====================
// LOADING HELPERS
// =====================
function setLoading(state = true) {
  document.body.style.opacity = state ? "0.6" : "1";
}

// =====================
// LOAD DASHBOARD
// =====================
async function loadDashboard() {
  setLoading(true);

  try {
    const res = await fetch(`${API}/analytics/kpis`);

    if (!res.ok) throw new Error("API error");

    const kpi = await res.json();

    document.getElementById("students").innerText = kpi.total_students ?? 0;
    document.getElementById("avg").innerText = kpi.avg_score ?? 0;
    document.getElementById("top").innerText = kpi.top_score ?? 0;
    document.getElementById("risk").innerText = kpi.at_risk ?? 0;

    await loadStudents();

  } catch (err) {
    console.error(err);
    alert("⚠️ Backend is waking up... try again in few seconds");
  }

  setLoading(false);
}

// =====================
// LOAD STUDENTS
// =====================
async function loadStudents() {
  try {
    const res = await fetch(`${API}/students`);

    if (!res.ok) throw new Error("Students API failed");

    const data = await res.json();

    const table = document.querySelector("#studentTable tbody");
    table.innerHTML = "";

    if (!data.length) {
      table.innerHTML = `<tr><td colspan="3">No data available</td></tr>`;
      return;
    }

    const names = [];
    const scores = [];

    data.forEach(s => {
      names.push(s.name || "N/A");
      scores.push(s.score || 0);

      const row = `
        <tr>
          <td>${s.name || "-"}</td>
          <td>${s.score || 0}</td>
          <td>${s.risk || "Low"}</td>
        </tr>
      `;
      table.innerHTML += row;
    });

    loadCharts(names, scores);

  } catch (err) {
    console.error(err);
  }
}

// =====================
// CHARTS
// =====================
let barChart, lineChart;

function loadCharts(labels, data) {

  if (barChart) barChart.destroy();
  if (lineChart) lineChart.destroy();

  barChart = new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Scores",
        data
      }]
    }
  });

  lineChart = new Chart(document.getElementById("lineChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Trend",
        data
      }]
    }
  });
}

// =====================
// CSV UPLOAD
// =====================
async function uploadCSV() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Select a CSV file");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setLoading(true);

  try {
    const res = await fetch(`${API}/upload`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Upload failed");

    alert("✅ Upload successful!");

    await loadDashboard();

  } catch (err) {
    console.error(err);
    alert("❌ Upload failed");
  }

  setLoading(false);
}
