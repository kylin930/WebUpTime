document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('responseTimeChart').getContext('2d');
    let chart;

    fetch('https://uptimeapi.devlab.icu/api/status')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // 更新表格内容
        const tbody = document.querySelector('#statusTable tbody');
        data.links.forEach((link, index) => {
            const row = `
            <tr>
            <td><img src="${data.icons[index]}" style="width: 24px; height: 24px;" /></td>
            <td><a href="${link}" target="_blank">${link}</a> (${data.names[index]})</td>
            <td><span class="${data.color[index]}">${data.check[index]}</span></td>
            <td>${data.one_day_uptime_rate[index]}%</td>
            <td>${data.uptime_rate[index]}%</td>
            <td>${data.down_count[index]}</td>
            <td>${data.checktime}</td>
            </tr>
            `;
            tbody.innerHTML += row;
        });

        // 绘制响应时间折线图
        const labels = Array.from(
            { length: Math.max(...data.response_times.map(arr => arr.length)) },
                                  (_, i) => `#${i + 1}`
        );
        const datasets = data.response_times.map((times, index) => ({
            label: data.links[index],
            data: times,
            borderColor: getRandomColor(),
                                                                    fill: false
        }));
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '响应时间统计 (单位: ms)'
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching the status data:', error));

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
});
