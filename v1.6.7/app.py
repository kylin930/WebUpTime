import tornado.ioloop
import tornado.web
import requests
import os
from threading import Thread
from urllib.parse import urlparse, urlunparse
from datetime import datetime,timedelta
import hashlib
import logging
import time
import json
import os

links = [
    "https://example.com",
    "https://baidu.com"
]
icons=[
    "",
    ""
]
names=[
    "example1",
    "example2"
]
ch = ["正常"]*len(links)
co = ["mdui-chip mdui-color-green"]*len(links)
error_messages = ["状态正常"] * len(links)
statuses = []
history_file = 'status_history.json'
down_file='down_count.json'
log_file = 'status_log.json'
uptime_rate = [0]*len(links)
one_day_uptime_rate = [0]*len(links)
prev_status = [1] * len(links)
down_count=[0]*len(links)
downout=[0]*len(links)
countdown=300
response_times = [[] for _ in range(len(links))]
header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0'
}

LOG_FILE = 'uptime.log'
handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

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

def load_daily_uptime_rate():
    if not os.path.exists("daily_uptime_rate.json"):
        return {}
    with open("daily_uptime_rate.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
        # 清理超过30天的数据
        thirty_days_ago = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        for link_idx in data:
            data[link_idx] = {date: rate for date, rate in data[link_idx].items() if date >= thirty_days_ago}
        return data

def save_daily_uptime_rate(daily_rates):
    with open("daily_uptime_rate.json", 'w', encoding='utf-8') as file:
        json.dump(daily_rates, file)

def load_status_log():
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}

def save_status_log(log_data):
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

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

def retry_request(url, headers, max_retries=2):
    backoff_factor = 1  # 指数退避基数，可以调整
    error_msg = ""
    derror = ""
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=(7, 5), headers=header)
            end_time = round((time.time() - start_time) * 1000, 2)
            print(f"{url}: {response.status_code}, 响应时间: {end_time}ms")
            return response, end_time, None
        except requests.exceptions.ConnectTimeout:
            error_msg = "请求超时（连接超时）"
            print(f"{url}: 请求超时（连接超时）")
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            print(f"{url}: 请求超时")
        except requests.exceptions.ConnectionError as e:
            error_msg = "连接错误"
            derror = f"{str(e)}"
            print(f"{url}: 连接错误")
        except requests.exceptions.SSLError:
            error_msg = "SSL证书验证失败"
            derror = f"{str(e)}"
            print(f"{url}: SSL证书验证失败")
        except requests.exceptions.RequestException as e:
            error_msg = "请求发生异常"
            derror = f"{str(e)}"
            print(f"{url}: 请求发生异常")
        if attempt < max_retries - 1:
            wait_seconds = backoff_factor * (2 ** attempt)  # 计算等待时间
            print(f"请求 {url} 失败，尝试第 {attempt + 1}/{max_retries} 次重试... 错误: {error_msg}，等待 {wait_seconds}s 后重试")
            time.sleep(wait_seconds)
        else:
            print(f"{url}: 所有重试均失败，最后一次错误: {error_msg}")
            return None, None, error_msg, derror
    return None, None, error_msg, derror

def webup():
    global ch
    global co
    global statuses
    global downout
    global uptime_rate
    global one_day_uptime_rate
    global error_messages
    global countdown
    global prev_status
    nowtime=datetime.now()
    countdown=-1
    temp=nowtime.strftime("%Y-%m-%d %H:%M")
    with open('tempfile.txt', 'w', encoding='utf-8') as file:
        file.write(temp)
    current_response_times = []
    statuses = []
    log_data = load_status_log()
    for i in range(len(links)):
        url = links[i]
        print(f"正在检查链接: {url}")
        response, end_time, error_msg, derror = retry_request(url, header)
        if str(i) not in log_data:
            log_data[str(i)] = []
        if response is not None and end_time is not None:
            status_code = response.status_code
            if status_code == 200:
                ch[i] = "正常"
                co[i] = "mdui-chip mdui-color-green"
                statuses.append(1)
                current_response_times.append(end_time)
                error_messages[i] = "状态正常"
                logging.info(f"{url}：正常, {end_time}ms")
                if prev_status[i] != 1:
                    log_entry = {
                        "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                        "url": url,
                        "event": "已恢复（Up）",
                        "message": "恢复正常访问"
                    }
                    log_data[str(i)].append(log_entry)
                    logging.info(f"{url}：已恢复")
                response.close()
            elif status_code in [301, 302]:
                ch[i] = "异常"
                co[i] = "mdui-chip mdui-color-red"
                statuses.append(0)
                current_response_times.append(end_time)
                error_messages[i] = f"页面被重定向: {status_code}"
                logging.info(f"{url}：重定向, {end_time}ms")
                response.close()
            else:
                ch[i] = "异常"
                co[i] = "mdui-chip mdui-color-red"
                statuses.append(0)
                current_response_times.append(None)
                error_messages[i] = f"状态码异常: {status_code}"
                response.close()
        else:
            ch[i] = "异常"
            co[i] = "mdui-chip mdui-color-red"
            statuses.append(0)
            current_response_times.append(None)
            error_messages[i] = error_msg if error_msg else "请求失败！两次重试均失败"
            logging.info(f"{url}：异常, {error_msg}")
            print(f"{url}: 请求失败")
            derror=derror.replace('\'', '')
            derror=derror.replace('"', '')
            derror=derror.replace('<', '')
            derror=derror.replace('>', '')
            if prev_status[i] != 0:
                log_entry = {
                    "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                    "url": url,
                    "event": "下线（Down）",
                    "message": error_msg or "未知错误"
                    "details": derror or "无"
                }
                log_data[str(i)].append(log_entry)
                logging.info(f"{url}：{error_msg}")
    save_status_log(log_data)
    prev_status = statuses[:]
    update_status_history(statuses)
    update_down(statuses)
    update_response_times(current_response_times)
    downout=load_down_counts()
    daily_uptime_rate = load_daily_uptime_rate()
    today = datetime.now().strftime("%Y-%m-%d")
    for i in range(len(links)):
        jisuan_uptime_rate(i)
        if str(i) not in daily_uptime_rate:
            daily_uptime_rate[str(i)] = {}
        daily_uptime_rate[str(i)][today] = one_day_uptime_rate[i]
    save_daily_uptime_rate(daily_uptime_rate)
    countdown=300
    print("30天在线率计算完成！")

def monitoring():
    while True:
        webup()
        time.sleep(300)

def cdtime():
    global countdown
    while True:
        if countdown == -1:
            while countdown != 300:
                time.sleep(1)
        else:
            countdown-=1
        time.sleep(1)

class getcd(tornado.web.RequestHandler):
    @enable_cors
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            'cd': countdown
        }))

class APIHandler(tornado.web.RequestHandler):
    @enable_cors
    def get(self):
        file_path = 'tempfile.txt'
        with open(file_path, 'r', encoding='utf-8') as file:
            checkt = file.read()
        daily_uptime_rate=load_daily_uptime_rate()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            'icons': icons,
            'links': links,
            'names': names,
            'uptime_rate': uptime_rate,
            'one_day_uptime_rate': one_day_uptime_rate,
            'daily_uptime_rate': daily_uptime_rate,
            'check': ch,
            'color': co,
            'down_count': downout,
            'cd': countdown,
            'response_times': response_times,
            'error_messages': error_messages,
            'checktime': checkt
        }))

class LogHandler(tornado.web.RequestHandler):
    @enable_cors
    def get(self):
        site_id = self.get_argument("id", default=None)
        log_data = load_status_log()

        if site_id and site_id in log_data:
            result = log_data[site_id]
        else:
            result = log_data

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(result, ensure_ascii=False))

def make_app():
    return tornado.web.Application([
        (r"/api/status", APIHandler),
        (r"/api/cd", getcd),
        (r"/api/log", LogHandler)
    ])

if __name__ == "__main__":
    thread1 = Thread(target=monitoring)
    thread1.start()
    thread2 = Thread(target=cdtime)
    thread2.start()
    app = make_app()
    app.listen(7332)
    print("HTTP服务端已运行在 http://127.0.0.1:7332")
    tornado.ioloop.IOLoop.current().start()
