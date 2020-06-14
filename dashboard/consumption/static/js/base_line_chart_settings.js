
function get_base_chart_config()
{
  return {
    type: 'line',
    data: {
      datasets: [{
        label: '',
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
        }]
      }
    }
  };
}

function create_chart(consumptions, element, is_total, color, label)
{
  var chart = new Chart(element, get_base_chart_config());
  chart.data.datasets[0].data = consumptions.map(
    function(consumption, index) {
      return {
        x: new Date(consumption['day']),
        y: parseFloat(consumption[ is_total ? 'day_total' : 'day_average' ]) 
      };
    }
  );
  chart.data.datasets[0].backgroundColor = 'rgba(' + color + ', 0.2)';
  chart.data.datasets[0].borderColor = 'rgba(' + color + ', 1)';
  chart.data.datasets[0].label = label;
  chart.update();
  return chart;
}