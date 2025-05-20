document.addEventListener('DOMContentLoaded', function () {
    let ctx = document.getElementById('responseTimeChart').getContext('2d');
    let chart;
    // 获取线性进度指示器和错误文本元素
    let loadingIndicator = document.getElementById('loadingIndicator');
    let errorText = document.getElementById('errorText');
    let refreshButton = document.getElementById('refreshButton');

    function getData() {
        let tbody = document.querySelector('#statusTable tbody');
        tbody.innerHTML = ''; // 清空
        loadingIndicator.style.display = 'block';
        errorText.style.display = 'none';

        fetch('https://uptimeapi.devlab.icu/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingIndicator.style.display = 'none';
            errorText.style.display = 'none';
            // 更新表格内容
            data.links.forEach((link, index) => {
                let row = `
                <div class="mdui-ripple">
                <tr>
                <td><img src="${data.icons[index]}" style="width: 24px; height: 24px;" /></td>
                <td><a href="${link}" target="_blank">${link}</a> (${data.names[index]})</td>
                <td><span class="${data.color[index]}" mdui-tooltip="{content: '${data.error_messages[index]}', position: 'top'}">${data.check[index]}</span></td>
                <td>${data.one_day_uptime_rate[index]}%</td>
                <td>${data.uptime_rate[index]}%</td>
                <td>${data.down_count[index]}</td>
                <td>${data.checktime}</td>
                </tr>
                </div>
                `;
                tbody.innerHTML += row;
            });

            // 更新折线图
            if (chart) {
                chart.destroy(); // 销毁旧的图表实例
            }
            // 绘制响应时间折线图
            let labels = Array.from(
                { length: Math.max(...data.response_times.map(arr => arr.length)) },
                                    (_, i) => `#${i + 1}`
            );

            let datasets = data.response_times.map((times, index) => ({
                label: data.links[index],
                data: times,
                borderColor: getRandomColor(),
                fill: false,
                hidden: true
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
                            display: false // 禁用Chart.js自带的图例
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
            let legendContainer = document.getElementById('legendContainer');
            legendContainer.innerHTML = ''; // 清空之前的图例

            data.links.forEach((link, index) => {
                let checkboxId = `legendCheckbox-${index}`;
                let isChecked = !datasets[index].hidden;
                let color = datasets[index].borderColor;

                let div = document.createElement('label');
                div.className = 'mdui-checkbox mdui-m-r-2';

                div.innerHTML = `
                <input type="checkbox" id="${checkboxId}" class="legend-checkbox" data-index="${index}" ${isChecked ? 'checked' : ''}>
                <i class="mdui-checkbox-icon"></i>
                <span style="color: ${color}; margin-left: 8px;">${link}</span>
                `;

                legendContainer.appendChild(div);
            });
            document.querySelectorAll('.legend-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', function () {
                    let datasetIndex = parseInt(this.getAttribute('data-index'));
                    let checked = this.checked;
                    chart.data.datasets[datasetIndex].hidden = !checked;
                    chart.update();
                });
            });
        })
        .catch(error => {
            console.error('Error fetching the status data:', error);

            // 隐藏进度条，显示错误文本
            loadingIndicator.style.display = 'none';
            errorText.style.display = 'block';
        });
    }

    getData();
    refreshButton.addEventListener('click', function () {
        getData();
    });

    function getRandomColor() {
        let letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
});
