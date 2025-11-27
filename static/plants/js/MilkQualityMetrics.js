async function fetchQualityMetrics() {
    const query = `
      query {
        milkLotVolumeStatsCurrentMonth {
          date
          status
          totalVolume
        }
      }
    `;

    const response = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
    });

    const result = await response.json();
    return result.data.milkLotVolumeStatsCurrentMonth;
}

async function renderQualityMetricsChart() {
    const rawData = await fetchQualityMetrics();

    // Aggregate volumes by status
    const aggregated = rawData.reduce((acc, item) => {
        if (!acc[item.status]) acc[item.status] = 0;
        acc[item.status] += item.totalVolume;
        return acc;
    }, {});

    const labels = Object.keys(aggregated);
    const volumes = Object.values(aggregated);

    const ctx = document.getElementById("qualityMetricsChart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Volume (Litres)",
                data: volumes,
                backgroundColor: ["#4CAF50", "#FFC107", "#F44336"], // green, yellow, red
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { mode: "index", intersect: false }
            },
            scales: {
                x: { title: { display: true, text: "Status" } },
                y: { title: { display: true, text: "Volume (Litres)" }, beginAtZero: true }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", renderQualityMetricsChart);
