import tornado.ioloop
import tornado.web
import requests
from threading import Thread
from datetime import datetime
import time

#下面这定义的两个数组都是初始值，不需要修改（如需修改状态的颜色就把co数组的每项默认值里的”green“改成对应颜色的英文，可参照MDUI的官方文档）
ch=["正常", "正常"]
co=["mdui-chip mdui-color-green", 
    "mdui-chip mdui-color-green"
    ]

# 以下为要监测的链接列表，自行修改
links=["https://example.com", 
       "https://baidu.com"
       ]
re=["", ""]

def webup():
    nowtime = datetime.now()
    temp = nowtime.strftime("%Y-%m-%d %H:%M")# 获取当前时间存入临时文件，不用全局变量存储是因为Py的太难用了
    with open('tempfile.txt', 'w', encoding='utf-8') as file:
        file.write(temp)
    
    i=0
    while (i < 2):
        re[i] = requests.get(links[i])
        if re[i].status_code == "200":# 如果返回的HTTP状态码不等于200就显示异常
            ch[i]="正常"
            co[i]="mdui-chip mdui-color-green"
        else:
            ch[i]="异常"
            co[i]="mdui-chip mdui-color-red"
        i += 1

def monitoring():
    while True:
        webup()
        time.sleep(60) #这里可以设置检查间隔的时间，单位为秒，默认是60秒

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        file_path = 'tempfile.txt'
        with open(file_path, 'r', encoding='utf-8') as file:#读取存储在临时文件里的时间
            checkt = file.read()
        self.render("index.html", 
                    sitename="网站状态监测", #此为网站的标题栏，也就是head元素里的title
                    title="网站状态监测", #此为网站的标题，显示在卡片的右上角
                    checktime=checkt, #此为上次检查时间，不会可以不用改
                    check1=ch[0], #底下这些都是用来渲染网站状态颜色和文字的，不需要改
                    check2=ch[1], 
                    color1=co[0], 
                    color2=co[1]
                    )

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ], template_path="./mub") #html模板存放路径

if __name__ == "__main__":
    thread=Thread(target=monitoring)
    thread.start() #新建线程防止死循环阻塞后面的脚本
    app = make_app()
    app.listen(7332) #http服务器端口
    print("HTTP服务端已运行在 http://127.0.0.1:7332")
    tornado.ioloop.IOLoop.current().start()
