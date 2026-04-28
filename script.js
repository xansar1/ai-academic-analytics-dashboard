const API = "https://ai-academic-backend.onrender.com/api";

// =====================
// LOADING
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
    alert("⚠️ Backend is waking up... wait 10 sec and refresh");
  }

  setLoading(false);
}

// =====================
// LOAD STUDENTS + AI
// =====================
async function loadStudents() {
  try {
    const res = await fetch(`${API}/students`);
    if (!res.ok) throw new Error("Students API failed");

    const data = await res.json();

    const table = document.querySelector("#studentTable tbody");
    const riskList = document.getElementById("riskList");
    const insightText = document.getElementById("insightText");

    table.innerHTML = "";
    riskList.innerHTML = "";

    if (!data.length) {
      table.innerHTML = `<tr><td colspan="4">No data available</td></tr>`;
      return;
    }

    const names = [];
    const scores = [];

    let highRisk = 0;
    let lowScoreCount = 0;

    data.forEach(s => {
      const name = s.name || "N/A";
      const score = s.score || 0;
      const risk = s.risk || "Low";

      names.push(name);
      scores.push(score);

      // 🔴 HIGH RISK LIST
      if (risk === "High") {
        highRisk++;
        riskList.innerHTML += `<li>⚠️ ${name} needs immediate attention</li>`;
      }

      // 📉 LOW SCORE DETECTION
      if (score < 50) lowScoreCount++;

      // ACTION BUTTON
      const actionBtn = `
        <button onclick="alert('Call parent of ${name}')">
          📞 Act
        </button>
      `;

      const row = `
        <tr>
          <td>${name}</td>
          <td>${score}</td>
          <td>${risk}</td>
          <td>${actionBtn}</td>
        </tr>
      `;

      table.innerHTML += row;
    });

    // =====================
    // AI INSIGHT
    // =====================
    if (highRisk > 0) {
      insightText.innerText =
        `🚨 ${highRisk} students are at HIGH risk. Immediate parent contact recommended.`;
    } else if (lowScoreCount > 0) {
      insightText.innerText =
        `📉 ${lowScoreCount} students scoring below 50. Conduct revision sessions.`;
    } else {
      insightText.innerText =
        "✅ All students performing well. Maintain current strategy.";
    }

    // =====================
    // EMPTY RISK STATE
    // =====================
    if (highRisk === 0) {
      riskList.innerHTML = "<li>✅ No high-risk students</li>";
    }

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

// =====================
// SEND ALERT
// =====================
function sendAlerts() {
  alert("📲 WhatsApp API connect cheythal automatic alert send aakum");
}
