const API = "https://ai-academic-backend.onrender.com/api";

// =====================
// LOAD DASHBOARD
// =====================
async function loadDashboard() {
  try {
    // KPIs
    const res = await fetch(`${API}/analytics/kpis`);
    const kpi = await res.json();

    document.getElementById("students").innerText = kpi.total_students;
    document.getElementById("avg").innerText = kpi.avg_score;
    document.getElementById("top").innerText = kpi.top_score;
    document.getElementById("risk").innerText = kpi.at_risk;

    // Students + Charts
    loadStudents();

  } catch (err) {
    console.error(err);
    alert("Backend connection error");
  }
}

// =====================
// LOAD STUDENTS
// =====================
async function loadStudents() {
  try {
    const res = await fetch(`${API}/students`);
    const data = await res.json();

    const table = document.querySelector("#studentTable tbody");
    table.innerHTML = "";

    const names = [];
    const scores = [];

    data.forEach(s => {
      names.push(s.name);
      scores.push(s.score);

      const row = `
        <tr>
          <td>${s.name}</td>
          <td>${s.score}</td>
          <td>${s.risk}</td>
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
      labels: labels,
      datasets: [{
        label: "Scores",
        data: data
      }]
    }
  });

  lineChart = new Chart(document.getElementById("lineChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Trend",
        data: data
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

  try {
    await fetch(`${API}/upload`, {
      method: "POST",
      body: formData
    });

    alert("Upload successful!");

    // refresh dashboard
    loadDashboard();

  } catch (err) {
    console.error(err);
    alert("Upload failed");
  }
}
