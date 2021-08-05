#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : https://www.bajins.com
# @Description : pythonw clock_sign.pyw
# @File : clock_sign.pyw
# @Version: 1.1.0
# @Time : 2020/7/26 11:00
# @Project: scripts_python
# @Package:
# @Software: PyCharm

"""
在C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp目录中创建一个network-reconnect.vbs文件，
把以下代码复制到其中并保存

Set Shell = CreateObject("WScript.Shell")
Shell.Run "pythonw clock_sign.pyw", 0, False
"""

import datetime
import re
import sched
import time

import requests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
             " Chrome/77.0.3865.75 Safari/537.36 "
# 去除警告
requests.packages.urllib3.disable_warnings()
# 如果请求失败默认重试次数
requests.adapters.DEFAULT_RETRIES = 5


def set_time(scheduler):
    # 延后1天的凌晨0点
    timestamp = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()
    # 设置运行时间
    scheduler.enterabs(timestamp, 0, run)


def run(range=1):
    if range == 10:  # 运行到第10次
        set_time(scheduler)
        return
    detect()
    scheduler.enter(60, 0, run, (range + 1,))  # 1分钟后再次运行


def detect():
    res = requests.get("https://www.bajins.com", headers={"User-Agent": USER_AGENT}, verify=False, timeout=600)
    if res.status_code != 200 or res is None:
        login()
        print(res.status_code)


def login():
    session = requests.sessions.Session()
    # 关闭多余的连接
    session.keep_alive = False
    session.headers["User-Agent"] = USER_AGENT
    session.verify = False
    session.timeout = 600
    res = session.get("http://192.168.10.253:8080/smsauth/3/pc.php?params=pwd&force_modify_password=")  # 登录页面
    cookie = ''
    for name, value in session.cookies.items():
        cookie += '{0}={1}'.format(name, value)
    session.headers["Referer"] = res.url
    session.headers["Cookie"] = cookie
    # 登录验证
    res = session.get("http://192.168.10.253:8080/login_check_password_ageout.php?username=temp004&passwd=temp004")
    res = session.get(session.headers["Referer"])  # 再次请求登录页面
    res = session.post("http://192.168.10.253:8080/cgi-bin/ace_web_auth.cgi?web_jumpto=&orig_referer="
                       "&username=temp004&userpwd=temp004&login_page=",
                       data={"username": "temp004", "userpwd": "temp004"})  # 获取登录验证token
    search = re.search("location = \"(.*)\"", res.text, re.I | re.M)
    if search:
        # http://192.168.10.253:8080/login_online_detail.php?show_portal=1&force_modify_password=0&orig_referer=&login_page=
        res = session.get("http://192.168.10.253:8080" + search.group(1))  # 通过token验证，并跳转到登录成功页面
    # 注销 http://192.168.10.253:8080/cgi-bin/ace_web_auth.cgi?logout=1&login_page=
    print(res.status_code)


if __name__ == '__main__':
    # import win32api, win32gui

    # ct = win32api.GetConsoleTitle()
    # hd = win32gui.FindWindow(0, ct)
    # win32gui.ShowWindow(hd, 0)
    detect()
    # 设置时间调度器
    scheduler = sched.scheduler(time.time, time.sleep)
    set_time(scheduler)
    # 运行函数
    scheduler.run()
