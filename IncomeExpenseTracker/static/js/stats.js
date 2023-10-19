const renderChart = (data, labels) => {
const ctx = document.getElementById('myChart').getContext('2d');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: 'Last 6 months expenses',
        data: data,
        borderWidth: 1
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Expenses per category'
      }
    }
  });
}

const getChartData = () => {
  fetch('expense-category-summary')
    .then((res) => res.json())
    .then((results) => {
      console.log('results', results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];

      renderChart(data, labels);
    });
};

window.onload = getChartData;
