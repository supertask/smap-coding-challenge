/*
 * Show total and average electricity cunsumption charts for all users.
 */
function show_user_consumption_charts(total_consumptions, average_consmptions)
{
  var total_chart = new Chart($("#user_total_consumption_chart"), get_base_chart_config());
  var average_chart = new Chart($("#user_average_consumption_chart"), get_base_chart_config());

  total_chart.data.datasets[0].data = total_consumptions.map(
    function(consumption, index) {
      return {
        x: new Date(consumption['day']),
        y: parseFloat(consumption['day_total']) 
      };
    }
  );
  average_chart.data.datasets[0].data = average_consmptions.map(
    function(consumption, index) {
      return {
        x: new Date(consumption['day']),
        y: parseFloat(consumption['day_average']) 
      };
    }
  );
  total_chart.update();
  average_chart.update();
}