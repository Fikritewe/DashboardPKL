const ctx2 = document.getElementById('doughnut');

new Chart(ctx2, {
  type: 'doughnut',
  data: {
    labels: ['RPL', 'TKJ', 'Animasi', 'Teknik Elektro', 'Teknik Informatika'],
    datasets: [{
      label: 'Jurusan',
      data: [5, 18, 1, 4, 3],
      borderWidth: 1
    }]
  }
});
