#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description: 
# @PreInstall: 
# @Author : https://www.bajins.com
# @File : kaggle_run.py
# @Version: 1.0.0
# @Time : 2021/7/11 10:18
# @Project: scripts_python
# @Package: 
# @Software: PyCharm

import os
import subprocess
import datetime
import queue
from queue import Queue
from threading import Timer
import sched
import time

# 初始化sched模块的 scheduler 类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

# 用两个定时任务，一个查内核列表和状态，一个执行提交内核
kernel_queue = Queue(maxsize=0)  # 存放内核执行状态


def query():
    """
    https://github.com/Kaggle/kaggle-api#installation
    https://github.com/Kaggle/kaggle-api#kernels
    其中cli后缀函数是用于shell中执行：
        kernel_pull(self, user_name, kernel_slug, kwargs)
        kernel_push(self, kernel_push_request, kwargs)
        kernel_output(self, user_name, kernel_slug, kwargs)
        kernels_list(self, page, page_size, dataset, competition, parent_…
        kernels_status(self, kernel)
        kernels_pull(self, kernel, path, metadata, quiet)
        kernel_status(self, user_name, kernel_slug, kwargs)
        kernels_initialize(self, folder)
        kernels_initialize_cli(self, folder)
        kernels_list_cli(self, mine, page, page_size, search, csv_display…
        kernels_output(self, kernel, path, force, quiet)
        kernels_output_cli(self, kernel, kernel_opt, path, force, quiet)
        kernels_pull_cli(self, kernel, kernel_opt, path, metadata)
        kernels_push(self, folder)
        kernels_push_cli(self, folder)
        kernels_status_cli(self, kernel, kernel_opt)
    """
    try:
        os.environ['KAGGLE_CONFIG_DIR'] = os.getcwd()  # 指定kaggle.json文件所在目录
        # os.environ['KAGGLE_USERNAME'] =
        # os.environ['KAGGLE_KEY'] =
        import kaggle
        from kaggle.rest import ApiException

        ka = kaggle.KaggleApi()
        # kaggle.ApiClient() # 使用方式在kaggle_api_extended.py第235行
        ka.authenticate()  # 鉴权，相当于登录
        # config_data = ka.read_config_file()  # 当前kaggle.json配置信息
        # print(ka.config, config_data, ka.config_values)

        user = ka.config_values[ka.CONFIG_NAME_USER]  # 获取当前用户

        kls = ka.kernels_list(user=user)  # 指定用户的内核
        print(kls)
        # kls_list = [kls[i:i + 6] for i in range(0, len(kls), 6)]
        for kl in kls:
            name = user + "/" + str(kl)
            try:
                res = ka.kernels_status(name)  # 获取内核运行状态
                if res["status"] == "complete":
                    kernel_queue.put_nowait({"ka": ka, "user": user, "name": name, "res": res})
            # print(ka.kernel_output(user, name))  # 获取内核输出

            except ApiException as e:
                print(name, e.status, e.reason)
        # 定时任务：刷新内核队列
        schedule.enter(90000, 0, query)
    except ImportError or ModuleNotFoundError:
        print('not install, start install...')
        call = subprocess.call(f'pip install kaggle', shell=True)
        if call != 0:
            raise


def push():
    """
    消费队列数据
    :return:
    """
    try:
        for i in range(6):
            kn = kernel_queue.get_nowait()
            print(kn)
            # ka = kn["ka"]
            # print(ka.kernels_pull(kn["name"], "."))  # 拉取内核
            # ka.kernel_pull(kn["user"], kn["name"])
            # ka.kernels_push(".")  # 提交文件夹中所有的内核
            kernel_queue.task_done()  # 消费任务完成
    except queue.Empty:
        # print((datetime.datetime.now() + datetime.timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S"))
        print("队列为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    schedule.enter(10 * 60 * 60, 1, push)  # 10小时后再次运行


if __name__ == '__main__':
    # run()
    # 第一个参数是时间间隔（单位是秒，只有秒），第二个参数是要调用的函数名，第三个参数是调用函数的参数(tuple)
    # t = Timer(inc, run, (inc,))
    # t.start()
    # 注意 sched 模块不是循环的，一次调度被执行后就结束了，如果想再执行，请再次 enter
    # 四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, query)
    schedule.enter(0, 1, push)
    schedule.run()
