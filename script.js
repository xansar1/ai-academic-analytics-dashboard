const API_BASE = "https://ai-academic-backend.onrender.com";

async function loadDashboard() {
  try {
    // KPI fetch
    const res = await fetch(`${API_BASE}/analytics/kpis`);
    const data = await res.json();

    document.getElementById("students").innerText = data.total_students;
    document.getElementById("avg").innerText = data.avg_score;
    document.getElementById("top").innerText = data.top_score;
    document.getElementById("risk").innerText = data.at_risk;

    // Load students
    loadStudents();

  } catch (err) {
    console.error(err);
    alert("Backend connection failed");
  }
}

async function uploadCSV() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    await fetch("https://ai-academic-backend.onrender.com/upload", {
      method: "POST",
      body: formData
    });

    alert("Upload successful!");
    loadDashboard(); // refresh data

  } catch (err) {
    console.error(err);
    alert("Upload failed");
  }
}

async function loadStudents() {
  try {
    const res = await fetch(`${API_BASE}/students`);
    const students = await res.json();

    const table = document.querySelector("#studentTable tbody");
    table.innerHTML = "";

    students.forEach(s => {
      const row = `
        <tr>
          <td>${s.name}</td>
          <td>${s.score}</td>
          <td>${s.risk}</td>
        </tr>
      `;
      table.innerHTML += row;
    });

    loadCharts(students);

  } catch (err) {
    console.error(err);
  }
}

function loadCharts(students) {
  const names = students.map(s => s.name);
  const scores = students.map(s => s.score);

  new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "Scores",
        data: scores
      }]
    }
  });

  new Chart(document.getElementById("lineChart"), {
    type: "line",
    data: {
      labels: names,
      datasets: [{
        label: "Trend",
        data: scores
      }]
    }
  });
}
