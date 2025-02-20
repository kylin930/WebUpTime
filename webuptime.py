import tornado.ioloop
import tornado.web
import requests
import os
from threading import Thread
from datetime import datetime
import time
import json
import os

ch=["正常", "正常", "正常", "正常", "正常", "正常", "正常", "正常", "正常"]
co=["mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green"
    ]

links=["https://xlbzi.cn", 
       "https://zuanshijia.top", 
       "https://awa.pw", 
       "https://kina.uno", 
       "https://blog.kfdzcoffee.cn", 
       "https://www.nekopara.uk", 
       "https://xiaoluo233.us.kg", 
       "https://lmem.cn", 
       "https://blog.ciy.cool"
       ]
re=["", "", "", "", "", "", "", "", ""]
statuses = []

history_file = 'status_history.json' # 存储状态历史记录的文件名

def load_history():# 加载本地存储的历史状态记录
    if not os.path.exists(history_file):
        return {}
    with open(history_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_history(history):# 保存历史状态记录到本地
    with open(history_file, 'w', encoding='utf-8') as file:
        json.dump(history, file)

def update_status_history(statuses):# 更新历史状态记录文件
    history = load_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for idx, status in enumerate(statuses):
        if str(idx) not in history:
            history[str(idx)] = []
        history[str(idx)].append((timestamp, status))
        # 保持只保留最近30天的数据
        history[str(idx)] = [entry for entry in history[str(idx)]
                             if (datetime.now() - datetime.strptime(entry[0], "%Y-%m-%d %H:%M")).days <= 30]
    save_history(history)

def webup():
    global ch
    global co
    global re
    global statuses
    nowtime=datetime.now()
    temp=nowtime.strftime("%Y-%m-%d %H:%M")
    with open('tempfile.txt', 'w', encoding='utf-8') as file:
        file.write(temp)
    statuses=[]
    i=0
    while i < len(links):
        try:
            try:
                re[i] = requests.get(links[i], timeout=(5,5))
                print(links[i] + ":" + str(re[i].status_code))
                if re[i].status_code == 200:
                    ch[i]="正常"
                    co[i]="mdui-chip mdui-color-green"
                    statuses.append(1)
                else:
                    ch[i]="异常"
                    co[i]="mdui-chip mdui-color-red"
                    statuses.append(0)
                update_status_history(statuses)
                i+=1
            except requests.exceptions.Timeout as e:
                # 捕获超时异常，并区分是连接超时还是读取超时
                if isinstance(e, requests.exceptions.ConnectTimeout):
                    print(links[i] + ":连接超时")
                elif isinstance(e, requests.exceptions.ReadTimeout):
                    print(links[i] + ":读取超时")
                ch[i]="异常"
                co[i]="mdui-chip mdui-color-red"
                statuses.append(0)
                update_status_history(statuses)
                i+=1
        except requests.exceptions.RequestException as e:
            print(links[i] + ":连接错误")
            ch[i]="异常"
            co[i]="mdui-chip mdui-color-red"
            statuses.append(0)
            update_status_history(statuses)
            i+=1
        except requests.exceptions.ConnectionError:
            print(links[i] + ":连接错误")
            ch[i]="异常"
            co[i]="mdui-chip mdui-color-red"
            statuses.append(0)
            update_status_history(statuses)
            i+=1

def monitoring():
    while True: 
        webup()
        time.sleep(300)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        uptime_rate = []
        history = load_history()
        for idx in range(len(links)):
            entries = history.get(str(idx), [])
            online_count = sum(entry[1] for entry in entries)
            total_entries = len(entries)
            uptime_rate.append(round(online_count / total_entries * 100, 2) if total_entries > 0 else 0)

        file_path = 'tempfile.txt'
        with open(file_path, 'r', encoding='utf-8') as file:
            checkt = file.read()
        self.render("index.html", 
                    sitename="友链状态监测", 
                    title="友链状态监测", 
                    checktime=checkt, 
                    check1=ch[0], 
                    check2=ch[1], 
                    check3=ch[2], 
                    check4=ch[3], 
                    check5=ch[4], 
                    check6=ch[5], 
                    check7=ch[6], 
                    check8=ch[7], 
                    check9=ch[8], 
                    color1=co[0], 
                    color2=co[1], 
                    color3=co[2], 
                    color4=co[3], 
                    color5=co[4], 
                    color6=co[5], 
                    color7=co[6], 
                    color8=co[7], 
                    color9=co[8],
                    uptime_rate1=uptime_rate[0],
                    uptime_rate2=uptime_rate[1],
                    uptime_rate3=uptime_rate[2],
                    uptime_rate4=uptime_rate[3],
                    uptime_rate5=uptime_rate[4],
                    uptime_rate6=uptime_rate[5],
                    uptime_rate7=uptime_rate[6],
                    uptime_rate8=uptime_rate[7],
                    uptime_rate9=uptime_rate[8]
                    )

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ], template_path="./mub")

if __name__ == "__main__":
    thread1=Thread(target=monitoring)
    thread1.start()
    app = make_app()
    app.listen(7332)
    print("HTTP服务端已运行在 http://127.0.0.1:7332")
    tornado.ioloop.IOLoop.current().start()
