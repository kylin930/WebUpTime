async function loadLogs() {
    try {
        var statusRes = await fetch('https://uptimeapi.devlab.icu/api/status');
        var statusData = await statusRes.json();

        var logRes = await fetch('https://uptimeapi.devlab.icu/api/log');
        var logData = await logRes.json();
        var tabContainer = document.getElementById('log-tabs');
        var contentContainer = document.getElementById('tab-content-container');
        statusData.names.forEach((name, index) => {
            var siteId = index.toString();
            let logs = logData[siteId] || [];
            // 按时间降序排序
            logs.sort((a, b) => new Date(b.time) - new Date(a.time));
            var tabLink = document.createElement('a');
            tabLink.href = `#tab-${siteId}`;
            tabLink.className = 'mdui-ripple';
            tabLink.textContent = name;
            tabContainer.appendChild(tabLink);
            var tabContent = document.createElement('div');
            tabContent.id = `tab-${siteId}`;
            tabContent.className = 'mdui-p-a-2';

            if (logs.length === 0) {
                var noLog = document.createElement('p');
                noLog.textContent = '暂无日志';
                tabContent.appendChild(noLog);
            } else {
                logs.forEach(log => {
                    var card = document.createElement('div');
                    card.className = 'mdui-card mdui-shadow-2 log-card';
                    var cardContent = document.createElement('div');
                    cardContent.className = 'mdui-card-content';
                    var icon = document.createElement('i');
                    icon.className = 'mdui-icon material-icons log-icon';
                    icon.textContent = log.event === '下线（Down）' ? 'arrow_downward' : 'arrow_upward';
                    icon.classList.add(log.event === '下线（Down）' ? 'down' : 'up');
                    var title = document.createElement('span');
                    title.textContent = log.event === '下线（Down）' ? '已下线（Down）' : '已恢复（Up）';
                    title.style.fontWeight = 'bold';
                    var time = document.createElement('div');
                    time.className = 'log-time';
                    time.textContent = log.time;
                    var details = document.createElement('div');
                    details.className = 'log-details';
                    var dt=log.details ? log.details : '无';
                    details.innerHTML = `<strong>原因：${log.message}</strong><br>详细错误：${dt}`;
                    cardContent.appendChild(icon);
                    cardContent.appendChild(title);
                    cardContent.appendChild(time);
                    cardContent.appendChild(details);
                    card.appendChild(cardContent);
                    tabContent.appendChild(card);
                });
            }
            contentContainer.appendChild(tabContent);
        });
        new mdui.Tab('#log-tabs');
    } catch (error) {
        console.error('加载日志数据失败:', error);
    }
}
window.onload = loadLogs;
