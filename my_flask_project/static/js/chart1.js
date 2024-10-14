const ctx = document.getElementById('barchart');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['RPL', 'TKJ', 'Animasi', 'Teknik Elektro', 'Teknik Informatika'],
      datasets: [{
        label: 'Jurusan',
        data: [5, 18, 1, 4, 3],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });