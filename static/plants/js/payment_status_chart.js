// plants/static/plants/js/payment_status_chart.js

async function fetchBillSummary() {
  const query = `
    query {
      billSummaryCurrentMonth {
        isPaid
        totalValue
        totalVolumeL
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
    return result.data.billSummaryCurrentMonth;
  } catch (error) {
    console.error("Error fetching bill summary:", error);
    return [];
  }
}

async function renderPaymentStatusChart() {
  const rawData = await fetchBillSummary();
  const labels = rawData.map(item => (item.isPaid ? "Paid" : "Unpaid"));
  const data = rawData.map(item => item.totalValue);

  const colors = [
    "rgba(75, 192, 192, 0.7)",  
    "rgba(255, 99, 132, 0.7)"   
  ];

  const borderColors = colors.map(c => c.replace("0.7", "1"));

  const ctx = document.getElementById("paymentStatusChart").getContext("2d");

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels.map((label, i) => `${label} (₹${data[i].toLocaleString()})`),
      datasets: [
        {
          data: data,
          backgroundColor: colors,
          borderColor: borderColors,
          borderWidth: 2,
          hoverOffset: 15
        }
      ]
    },
    options: {
      responsive: true,
      cutout: "65%", 
      plugins: {
        legend: {
          position: "right",
          labels: {
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const label = context.label || "";
              const value = context.parsed.toLocaleString();
              return `${label}: ₹${value}`;
            }
          }
        },
        title: {
          display: true,
          text: "Paid vs Unpaid Bills (₹ Value, Current Month)",
          font: { size: 16, weight: "bold" }
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", renderPaymentStatusChart);
