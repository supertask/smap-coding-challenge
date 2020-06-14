
function get_base_chart_config()
{
  return {
    type: 'line',
    data: {
      datasets: [{
        label: 'Total electricity consumption',
        data: [],
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255,99,132,1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        xAxes: [{
          type: 'time',
          position: 'bottom',
          displayFormats: { 'day': 'MMM DD' }
        }],
        yAxes: [{
          ticks: {
            min: 0,
            max: 3000000,
            stepSize: 500000
          }
        }]
      }
    }
  };
}