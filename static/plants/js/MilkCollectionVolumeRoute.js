async function loadRouteVolumePieChart() {
  try {
    const response = await fetch("/graphql/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: `
          query {
            milkLotVolumeByRoute {
              routeName
              totalVolume
            }
          }
        `,
      }),
    });

    const result = await response.json();
    const data = result.data.milkLotVolumeByRoute;

    // Extract labels and values
    const labels = data.map(item => item.routeName);
    const volumes = data.map(item => item.totalVolume);

    const ctx = document.getElementById("routeVolumeChart").getContext("2d");

    // Create Pie Chart
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          label: "Collection Volume (Litres)",
          data: volumes,
          backgroundColor: [
            "#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#E91E63", "#00BCD4"
          ],
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "right",
          },
          title: {
            display: true,
            text: "Milk Collection by Region (Current Month)"
          }
        }
      }
    });

  } catch (error) {
    console.error("Error loading route volume chart:", error);
  }
}

// Call the function on page load
document.addEventListener("DOMContentLoaded", loadRouteVolumePieChart);