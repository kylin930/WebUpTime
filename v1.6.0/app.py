import tornado.ioloop
import tornado.web
import requests
import os
from threading import Thread
from urllib.parse import urlparse, urlunparse
from datetime import datetime,timedelta
import hashlib
import time
import json
import os

ch = ["正常"]*11
co = ["mdui-chip mdui-color-green"]*11
links = [
    "https://example.com",
    "https://baidu.com"
]
icons=[
    "https://www.xiaorin.com/Image.jpg",
    "https://www.baidu.com/favicon.ico"
]
names=[
    "baidu",
    "example",
]
statuses = []
history_file = 'status_history.json'
down_file='down_count.json'
uptime_rate = [0]*len(links)
one_day_uptime_rate = [0]*len(links)
down_count=[0]*len(links)
downout=[0]*len(links)
response_times = [[] for _ in range(len(links))]

def enable_cors(func):
    def wrapper(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        if self.request.method == "OPTIONS":
            self.write({})
            self.set_status(204)
            self.finish()
        else:
            return func(self, *args, **kwargs)
    return wrapper

def load_history():
    if not os.path.exists(history_file):
        return {}
    with open(history_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_history(history):
    with open(history_file, 'w', encoding='utf-8') as file:
        json.dump(history, file)

def load_down_counts():
    if not os.path.exists(down_file):
        return {str(i): 0 for i in range(len(links))}  # 初始化
    with open(down_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_down_counts(counts):
    with open(down_file, 'w', encoding='utf-8') as file:
        json.dump(counts, file)

def load_response_time():
    if not os.path.exists("response_times.json"):
        return {str(i): [] for i in range(len(links))}  # 初始化为空列表
    with open("response_times.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
        for idx in range(len(links)):
            if str(idx) not in data or not isinstance(data[str(idx)], list):
                data[str(idx)] = []
        return data

def save_response_time(times):
    with open("response_times.json", 'w', encoding='utf-8') as file:
        json.dump(times, file)

def update_response_times(times):
    global response_times
    stored_times = load_response_time()
    for idx, time_value in enumerate(times):
        if time_value is not None:  # 只记录有效的响应时间
            if str(idx) not in stored_times:
                stored_times[str(idx)] = []  # 如果不存在，则初始化为空列表
            stored_times[str(idx)].append(time_value)
            stored_times[str(idx)] = stored_times[str(idx)][-50:]  # 最多保留最近 50 条记录
    response_times = [stored_times[str(i)] for i in range(len(links))]
    save_response_time(stored_times)

def update_status_history(statuses):
    history = load_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for idx, status in enumerate(statuses):
        if str(idx) not in history:
            history[str(idx)] = []
        history[str(idx)].append((timestamp, status))
        history[str(idx)] = [entry for entry in history[str(idx)]
                             if (datetime.now() - datetime.strptime(entry[0], "%Y-%m-%d %H:%M")).days <= 30]
    save_history(history)

def jisuan_uptime_rate(link_idx):
    global uptime_rate
    global one_day_uptime_rate

    history = load_history()
    entries = history.get(str(link_idx), [])

    online_count = sum(entry[1] for entry in entries)
    total_entries = len(entries)
    uptime_rate[link_idx] = round(online_count / total_entries * 100, 2) if total_entries > 0 else 0

    one_day_ago = datetime.now() - timedelta(days=1)
    recent_entries = [entry for entry in entries if datetime.strptime(entry[0], "%Y-%m-%d %H:%M") >= one_day_ago]
    online_count_recent = sum(entry[1] for entry in recent_entries)
    total_entries_recent = len(recent_entries)
    one_day_uptime_rate[link_idx] = round(online_count_recent / total_entries_recent * 100, 2) if total_entries_recent > 0 else 0

def update_down(statuses):
    global down_counts
    counts = load_down_counts()
    for idx, status in enumerate(statuses):
        if status == 0:  # 如果状态异常
            counts[str(idx)] += 1
    down_counts = [counts[str(i)] for i in range(len(links))]
    save_down_counts(counts)#更新Down计数文件

def webup():
    global ch
    global co
    global statuses
    global downout
    global uptime_rate
    global one_day_uptime_rate
    nowtime=datetime.now()
    temp=nowtime.strftime("%Y-%m-%d %H:%M")
    with open('tempfile.txt', 'w', encoding='utf-8') as file:
        file.write(temp)
    current_response_times = []
    statuses = []
    for i in range(len(links)):
        try:
            start_time = time.time()
            response = requests.get(links[i], timeout=(7, 5))
            end_time = round((time.time() - start_time) * 1000, 2)  # 转换为毫秒
            print(f"{links[i]}: {response.status_code}, 响应时间: {end_time}ms")

            if response.status_code == 200  or response.status_code == 301 or response.status_code == 302:
                ch[i] = "正常"
                co[i] = "mdui-chip mdui-color-green"
                statuses.append(1)
                current_response_times.append(end_time)
            else:
                ch[i] = "异常"
                co[i] = "mdui-chip mdui-color-red"
                statuses.append(0)
                current_response_times.append(None)
        except requests.exceptions.RequestException as e:
            print(f"{links[i]}: 连接错误")
            ch[i] = "异常"
            co[i] = "mdui-chip mdui-color-red"
            statuses.append(0)
            current_response_times.append(None)
    update_status_history(statuses)
    update_down(statuses)
    update_response_times(current_response_times)
    downout=load_down_counts()
    for i in range(len(links)):
        jisuan_uptime_rate(i)
    print("30天在线率计算完成！")

def monitoring():
    while True:
        webup()
        time.sleep(300)

class APIHandler(tornado.web.RequestHandler):
    @enable_cors
    def get(self):
        file_path = 'tempfile.txt'
        with open(file_path, 'r', encoding='utf-8') as file:
            checkt = file.read()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            'icons': icons,
            'links': links,
            'names': names,
            'uptime_rate': uptime_rate,
            'one_day_uptime_rate': one_day_uptime_rate,
            'check': ch,
            'color': co,
            'down_count': downout,
            'response_times': response_times,
            'checktime': checkt
        }))

def make_app():
    return tornado.web.Application([
        (r"/api/status", APIHandler),
    ])

if __name__ == "__main__":
    thread1 = Thread(target=monitoring)
    thread1.start()
    app = make_app()
    app.listen(7332)
    print("HTTP服务端已运行在 http://127.0.0.1:7332")
    tornado.ioloop.IOLoop.current().start()
