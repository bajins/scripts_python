#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description:
# @PreInstall:
# @Author : https://www.bajins.com
# @File : schedu.py
# @Version: 1.0.0
# @Time : 2020/1/11 22:09
# @Project: python_learning
# @Package:
# @Software: PyCharm
import datetime
import random
import sched
import subprocess
import time
from threading import Timer


class Demo(object):

    def __init__(self, cmd: str):
        _scheduler = sched.scheduler(time.time, time.sleep)
        _scheduler.enter(0, 0, self.run, (cmd, _scheduler,))  # 0为立即运行
        _scheduler.run()

    @staticmethod
    def run(command: str, _scheduler: sched.scheduler):
        # 执行shell命令并实时输出回显
        process = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT)
        # 判断子进程是否结束
        while process.poll() is None:
            if process.stdout is None:
                continue
            line = process.stdout.readline()
            line = line.strip()
            if line:
                print(line.decode("utf8", 'ignore'))
        # 明天的指定时间范围内随机时间执行
        timestamp = (datetime.datetime.now() + datetime.timedelta(days=1)
                     ).replace(hour=random.randint(8, 23), minute=random.randint(0, 60)).timestamp()
        _scheduler.enterabs(timestamp, 0, Demo.run, (command, _scheduler,))


def run():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == '__main__':
    # 初始化sched模块的 scheduler 类，设置时间调度器
    scheduler = sched.scheduler(time.time, time.sleep)
    # 延后1天的凌晨0点
    timestamp = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=0, minute=6, second=0, microsecond=0).timestamp()
    # 四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给该触发函数的参数（tuple形式）
    # 注意 sched 模块不是循环的，一次调度被执行后就结束了，如果想再执行，请再次 enter
    scheduler.enter(0, 0, run)  # 0为立即运行
    # 设置在指定的时间运行
    scheduler.enterabs(timestamp, 0, run)
    # 运行函数
    scheduler.run()

    ##########################

    # 第一个参数是时间间隔（单位是秒，只有秒），第二个参数是要调用的函数名，第三个参数是调用函数的参数(tuple)
    t = Timer(6, run, (1,))
    t.start()
