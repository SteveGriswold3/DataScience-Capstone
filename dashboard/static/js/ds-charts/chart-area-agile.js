// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Area Chart Example
var ctx = document.getElementById("myAgileAreaChart");
var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", "Day 11", "Day 12", "Day 13"],
    datasets: [{
      label: "Plan",
      lineTension: 0.3,
      backgroundColor: "rgba(2,216,0,0.2)",
      borderColor: "rgba(2,216,0,1)",
      pointRadius: 5,
      pointBackgroundColor: "rgba(2,216,0,1)",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "rgba(2,216,0,1)",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: [19, 17, 16, 15, 14, 13, 12, 10, 8, 6, 4, 2 , 0],
    },
    {
      label: "Actual",
      lineTension: 0.3,
      backgroundColor: "rgba(255,128,0,0.2)",
      borderColor: "rgba(255,128,0,1)",
      pointRadius: 5,
      pointBackgroundColor: "rgba(255,128,0,1)",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "rgba(255,128,0,1)",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: [19, 18, 15, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14],
    }
    ],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 20,
          maxTicksLimit: 5
        },
        gridLines: {
          color: "rgba(0, 0, 0, .125)",
        }
      }],
    },
    legend: {
      display: false
    }
  }
});
