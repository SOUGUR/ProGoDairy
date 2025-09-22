// plants/static/plants/js/milk_volume_chart.js
// Volume of Milk Collected in Litres Vs Date Collected  
async function fetchMilkLotVolume() {
  const query = `
    query {
      milkLotVolumeStatsCurrentMonth {
        date
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
    return result.data.milkLotVolumeStatsCurrentMonth;
  } catch (error) {
    console.error("Error fetching milk lot volume:", error);
    return [];
  }
}

async function renderMilkVolumeGraph() {
  const rawData = await fetchMilkLotVolume();

  const grouped = {};
  rawData.forEach(item => {
    if (!grouped[item.status]) {
      grouped[item.status] = [];
    }
    grouped[item.status].push({ date: item.date, volume: item.totalVolume });
  });

  const allDates = [...new Set(rawData.map(item => item.date))].sort(
    (a, b) => new Date(a) - new Date(b)
  );

  const statusColors = {
    approved: "rgba(75, 192, 192, 1)",
    pending: "rgba(255, 206, 86, 1)",
    rejected: "rgba(255, 99, 132, 1)"
  };

  const datasets = Object.keys(grouped).map(status => {
    const volumes = allDates.map(date => {
      const entry = grouped[status].find(d => d.date === date);
      return entry ? entry.volume : 0;
    });

    return {
      label: `${status.charAt(0).toUpperCase() + status.slice(1)} Volume`,
      data: volumes,
      backgroundColor: statusColors[status],
      borderColor: statusColors[status],
      borderWidth: 1,
      barPercentage: 0.3,     
      categoryPercentage: 0.8, 
      borderRadius: 2,         
    };
  });

  const ctx = document.getElementById("milkVolumeChart").getContext("2d");

  new Chart(ctx, {
    type: "bar", 
    data: {
      labels: allDates,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true, position: "top" },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y} L`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: "Date" },
          ticks: {
            maxRotation: 45,
            minRotation: 45,
            autoSkip: false 
          }
        },
        y: {
          title: { display: true, text: "Volume (Litres)" },
          beginAtZero: true
        }
      },
      
      layout: {
        padding: {
          left: 10,
          right: 10
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", renderMilkVolumeGraph);
