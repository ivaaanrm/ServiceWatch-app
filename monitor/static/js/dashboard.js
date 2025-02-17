let socket = null;
let currentRange = 'live';

const ctx = document.getElementById('resourcesChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'CPU %',
            data: [],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            tension: 0.1,
            fill: true
        }, {
            label: 'Memory %',
            data: [],
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            tension: 0.1,
            fill: true
        }, {
            label: 'Disk %',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.1,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    drawBorder: false
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

function connectWebSocket() {
    socket = new WebSocket('ws://' + window.location.host + '/ws/system_stats/');
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        updateChartWithLiveData(data);
        updateServicesList(data.services);
    };

    socket.onclose = function() {
        // Attempt to reconnect if connection was closed unexpectedly
        if (currentRange === 'live') {
            setTimeout(connectWebSocket, 1000);
        }
    };
}

function updateChartWithLiveData(data) {
    const now = new Date().toLocaleTimeString();
    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(data.cpu_percent);
    chart.data.datasets[1].data.push(data.memory_percent);
    chart.data.datasets[2].data.push(data.disk_percent);
    
    // Keep only last 30 data points for live view
    if (chart.data.labels.length > 30) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    chart.update();
}

function updateServicesList(services) {
    const servicesList = document.getElementById('servicesList');
    servicesList.innerHTML = services.map(service => 
        `<div class="service-item">
            <span class="service-name">${service.name}</span>
            <span class="badge ${service.status === 'running' ? 'bg-success' : 'bg-warning'}">${service.status}</span>
         </div>`
    ).join('');
}

async function fetchHistoricalData(range) {
    try {
        const response = await fetch(`/api/system-metrics/?range=${range}`);
        const data = await response.json();
        
        chart.data.labels = data.timestamps;
        chart.data.datasets[0].data = data.cpu;
        chart.data.datasets[1].data = data.memory;
        chart.data.datasets[2].data = data.disk;
        
        chart.update();
    } catch (error) {
        console.error('Error fetching historical data:', error);
    }
}

// Handle time range selection
document.querySelectorAll('[data-range]').forEach(button => {
    button.addEventListener('click', async function() {
        // Update active button state
        document.querySelectorAll('[data-range]').forEach(btn => 
            btn.classList.remove('active'));
        this.classList.add('active');
        
        const range = this.dataset.range;
        currentRange = range;
        
        // Handle WebSocket connection based on range
        if (range === 'live') {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                connectWebSocket();
            }
            // Clear existing data
            chart.data.labels = [];
            chart.data.datasets.forEach(dataset => dataset.data = []);
        } else {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
            await fetchHistoricalData(range);
        }
    });
});

// Initial connection for live data
connectWebSocket();