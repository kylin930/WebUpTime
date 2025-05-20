let remainingSeconds = 0;
let pollingInterval = null;

async function fetchData() {
    try {
        var response = await fetch('https://uptimeapi.devlab.icu/api/status');
        var data = await response.json();

        var app = document.getElementById('app');
        app.innerHTML = '';
        remainingSeconds = data.cd;

        data.links.forEach((link, index) => {
            var dailyUptimeRate = data.daily_uptime_rate[index] || {};
            var linkContainer = document.createElement('div');
            var title = document.createElement('h3');
            title.textContent = data.names[index];
            linkContainer.appendChild(title);
            var capsulesContainer = document.createElement('div');

            // 获取最近 30 天的日期
            var today = new Date();
            var last30Days = [];
            for (let i = 0; i < 30; i++) {
                var date = new Date(today);
                date.setDate(today.getDate() - i);
                last30Days.unshift(date.toISOString().split('T')[0]);
            }

            last30Days.forEach(date => {
                var rate = dailyUptimeRate[date];
                var capsuleWrapper = document.createElement('span');
                capsuleWrapper.className = 'tooltip';

                var capsule = document.createElement('div');
                capsule.className = 'capsule';
                capsule.style.backgroundColor = rate !== undefined ? getRateColor(rate) : '#9e9e9e';

                var tooltipText = document.createElement('span');
                tooltipText.className = 'tooltiptext';
                tooltipText.textContent = rate !== undefined ? `${date}: ${rate}%` : `${date}: 无数据`;

                capsuleWrapper.appendChild(capsule);
                capsuleWrapper.appendChild(tooltipText);
                capsulesContainer.appendChild(capsuleWrapper);
            });

            linkContainer.appendChild(capsulesContainer);
            app.appendChild(linkContainer);
        });

        updateCountdownDisplay();
    } catch (error) {
        console.error("Error fetching status:", error);
    }
}

function getRateColor(rate) {
    if (rate >= 97) return "#4caf50";
    if (rate >= 95) return "#57e389";
    if (rate >= 80) return "#ffeb3b";
    if (rate >= 0) return "#f66151";
    return '#9e9e9e';
}

function updateCountdownDisplay() {
    var countdownElement = document.getElementById('sec');
    if (remainingSeconds === -1) {
        startPolling();
    } else {
        stopPolling();
        countdownElement.textContent = `下次监测倒计时: ${remainingSeconds} 秒`;
    }
}

// 轮询cd接口
function startPolling() {
    var countdownElement = document.getElementById('sec');
    countdownElement.textContent = "监测中...约10秒左右";

    if (!pollingInterval) {
        pollingInterval = setInterval(async () => {
            try {
                var res = await fetch('https://uptimeapi.devlab.icu/api/cd');
                var data = await res.json();
                var newCd = data.cd;

                if (newCd !== -1) {
                    remainingSeconds = newCd;
                    stopPolling();
                    startCountdown(); // 重新开始倒计时
                }
            } catch (error) {
                console.error("Error polling /cd endpoint:", error);
            }
        }, 5000);
    }
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

function startCountdown() {
    var countdownElement = document.getElementById('sec');
    countdownElement.textContent = `下次监测倒计时: ${remainingSeconds} 秒`;
}
fetchData();

setInterval(() => {
    var countdownElement = document.getElementById('sec');

    if (remainingSeconds > 0 && remainingSeconds !== -1) {
        remainingSeconds--;
        countdownElement.textContent = `下次监测倒计时: ${remainingSeconds} 秒`;
    } else if (remainingSeconds === 0) {
        fetchData();
    }
}, 1000);
