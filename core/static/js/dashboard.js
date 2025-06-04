document.addEventListener('DOMContentLoaded', function() {
    // Gráfico de Citas por Día
    const citasChart = document.getElementById('citasChart');
    if (citasChart) {
        new Chart(citasChart.getContext('2d'), {
            type: 'line',
            data: {
                labels: JSON.parse(citasChart.dataset.fechas),
                datasets: [{
                    label: 'Citas Programadas',
                    data: JSON.parse(citasChart.dataset.citas),
                    fill: false,
                    borderColor: '#4361EE',
                    backgroundColor: '#4361EE',
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#4361EE',
                    pointBorderColor: '#fff',
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Actualización automática
    function actualizarEstadisticas() {
        fetch('/api/dashboard/stats/')
            .then(response => response.json())
            .then(data => {
                // Actualizar contadores
                document.querySelector('.card-citas-hoy .stat-number').textContent = data.citas_hoy;
                document.querySelector('.card-en-espera .stat-number').textContent = data.pacientes_espera;
                document.querySelector('.card-atendidos .stat-number').textContent = data.citas_completadas;
                document.querySelector('.card-total-pacientes .stat-number').textContent = data.total_pacientes;
                
                // Actualizar gráfico si existe
                if (citasChart && data.citas_por_dia) {
                    const chart = Chart.getChart(citasChart);
                    if (chart) {
                        chart.data.datasets[0].data = data.citas_por_dia;
                        chart.update();
                    }
                }
            })
            .catch(error => console.error('Error actualizando estadísticas:', error));
    }

    // Actualizar cada 5 minutos
    setInterval(actualizarEstadisticas, 300000);
});