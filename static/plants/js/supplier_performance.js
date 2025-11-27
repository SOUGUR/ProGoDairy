async function fetchSupplierStats() {
  const query = `
    query {
      supplierMilkVolumeStatsCurrentMonth {
        supplierId
        supplierName
        status
        totalVolume
      }
    }
  `;

  try {
    const response = await fetch("/graphql/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const result = await response.json();
    return result.data.supplierMilkVolumeStatsCurrentMonth;
  } catch (error) {
    console.error("Error fetching supplier stats:", error);
    return [];
  }
}

async function renderSupplierBarChart() {
  const rawData = await fetchSupplierStats();

  // Group by supplierId + supplierName
  const supplierTotals = {};
  rawData.forEach(item => {
    const key = `${item.supplierName} (ID: ${item.supplierId})`;
    if (!supplierTotals[key]) {
      supplierTotals[key] = 0;
    }
    supplierTotals[key] += item.totalVolume;
  });

  const labels = Object.keys(supplierTotals);
  const data = labels.map(supplier => supplierTotals[supplier]);

  const colors = [
    "rgba(75, 192, 192, 0.7)",
    "rgba(255, 99, 132, 0.7)",
    "rgba(255, 206, 86, 0.7)",
    "rgba(54, 162, 235, 0.7)",
    "rgba(153, 102, 255, 0.7)",
    "rgba(255, 159, 64, 0.7)"
  ];
  const borderColors = colors.map(c => c.replace("0.7", "1"));

  const ctx = document.getElementById("supplierChart").getContext("2d");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Total Volume Supplied (Litres)",
        data: data,
        backgroundColor: colors,
        borderColor: borderColors,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: "Milk Supplied per Supplier (Current Month)",
          font: { size: 16, weight: "bold" }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.parsed.y.toLocaleString()} L`;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { autoSkip: false, maxRotation: 45, minRotation: 0 },
          title: { display: true, text: "Suppliers" }
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "Volume (Litres)" }
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", renderSupplierBarChart);
