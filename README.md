# WebUpTime
一个使用Python做后端的http(s)网站监测程序
# 如何修改本项目的代码
py脚本我都写上注释了，以下是html渲染模板的修改帮助：
默认html模板（模板路径为mub/index.html）里的{{ xxx }}代表的是变量，可以在Python的脚本里给它赋值，赋值后会显示到html里

## 示例：
比如我在html模板里定义一个example变量
![image](https://github.com/user-attachments/assets/cf79b0a5-4580-4d78-9850-c3cfe3a865d7)
然后在Python脚本里的self.render()函数加上这个参数，等号左边为在html模板中定义的变量，右边为在Python脚本里定义的变量或字符串
![image](https://github.com/user-attachments/assets/a0a48b3a-e034-4280-be2f-ba2ce02da1c8)
## Python脚本运行结果：
![image](https://github.com/user-attachments/assets/63c7e6f6-a732-4905-b0dd-e0f6730af5ac)
好了，html模板修改的基础教程就这些了，其它的也挺少用（
如果要看更多的html模板语法，请参阅<https://www.osgeo.cn/tornado/guide/templates.html>
