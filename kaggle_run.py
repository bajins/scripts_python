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

import json
import os
import re
import shutil
import subprocess
import datetime
import queue
from queue import Queue
from threading import Timer
import sched
import time

os.environ['KAGGLE_CONFIG_DIR'] = os.getcwd()  # 指定kaggle.json文件所在目录
# os.environ['KAGGLE_USERNAME'] =
# os.environ['KAGGLE_KEY'] =
import kaggle
from kaggle.rest import ApiException

# 初始化sched模块的 scheduler 类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

# 用两个定时任务，一个查内核列表和状态并提交内核，一个执行本地的内核文件提交
pull_kernel_queue = Queue(maxsize=0)  # 存放内核执行状态
pull_run_qty = 6
local_kernel_queue = Queue(maxsize=0)  # 存放本地内核信息


def get_ka():
    """
    获取api实例
    https://github.com/Kaggle/kaggle-api#installation
    :return:
    """
    ka = kaggle.KaggleApi()
    # kaggle.ApiClient() # 使用方式在kaggle_api_extended.py第235行
    ka.authenticate()  # 鉴权，相当于登录
    # config_data = ka.read_config_file()  # 当前kaggle.json配置信息
    # print(ka.config, config_data, ka.config_values)
    return ka


def get_kernels():
    """
    获取配置信息、用户、内核
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
    ka = get_ka()
    user = ka.config_values[ka.CONFIG_NAME_USER]  # 获取当前用户
    kls = ka.kernels_list(user=user)  # 指定用户的内核
    return ka, kls, user


def download_kernels():
    """
    下载所有内核
    :return:
    """
    ka, kls, user = get_kernels()
    print(kls)
    # kls_list = [kls[i:i + 6] for i in range(0, len(kls), 6)]
    for kl in kls:
        name = re.sub(r"\.|_", "-", str(kl))  # 只能包含字母数字和-
        fully_name = user + "/" + name
        try:
            res = ka.kernels_status(fully_name)  # 获取内核运行状态
            print(res)
            ka.kernels_pull(fully_name, "kaggle_kernels")
        except ApiException as e:
            print(fully_name, e.status, e.reason)


def pull_push():
    """
    下载元数据并推送
    :return:
    """
    ka, kls, user = get_kernels()
    print(kls)
    # kls_list = [kls[i:i + 6] for i in range(0, len(kls), 6)]
    running_qty = 0
    for kl in kls:
        name = re.sub(r"\.|_", "-", str(kl))  # 只能包含字母数字和-
        fully_name = user + "/" + name
        try:
            res = ka.kernels_status(fully_name)  # 获取内核运行状态
            if res["status"] == "running":
                running_qty += 1
            else:  # "complete" or "error"
                pull_kernel_queue.put_nowait({"fully_name": fully_name, "name": name, "res": res})
        except ApiException as e:
            print(fully_name, e.status, e.reason)
    if 6 >= running_qty > 0:
        global pull_run_qty
        pull_run_qty -= running_qty

    # ==================
    # 消费队列数据，进行推送
    # ==================
    if pull_run_qty == 0:
        schedule.enter(10 * 60 * 60, 1, pull_push)  # 10小时后再次运行
        return
    qty = pull_run_qty
    if pull_kernel_queue.qsize() < pull_run_qty:
        qty = pull_kernel_queue.qsize()
    kernel_path = "./kaggle_code"
    try:
        for i in range(qty):
            kn = pull_kernel_queue.get_nowait()
            print(kn)
            path = kernel_path + "/" + kn["name"]
            try:
                ka.kernels_pull(kn["fully_name"], path, metadata=True)  # 拉取内核
                if os.path.exists(path):
                    ka.kernels_push(path)  # 提交文件夹中所有的内核
                    shutil.rmtree(path)  # 删除目录下的文件
            except ApiException as e:
                print(kn["fully_name"], e.status, e.reason)
                # kernels_initialize(ka, kn["name"], kernel_path)  # 初始化
        pull_kernel_queue.task_done()  # 消费任务完成
        schedule.enter(30 * 60 * 60, 1, pull_push)  # 30小时后再次运行
    except queue.Empty:
        # print((datetime.datetime.now() + datetime.timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S"))
        print("队列为空", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        schedule.enter(10 * 60 * 60, 1, pull_push)  # 10小时后再次运行


def local_push():
    """
    本地推送
    :return:
    """
    ka = get_ka()
    kernel_path = "./kaggle_code"
    if not os.path.exists(kernel_path) or not os.path.isdir(kernel_path):
        raise ValueError('Invalid folder: ' + kernel_path)
    for i in os.listdir(kernel_path):
        temp_dir = os.path.join(kernel_path, i)
        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            if re.search(r"[^a-zA-Z0-9-]+", i, re.I | re.M):
                print("文件夹名只能包含字母数字和-")
                continue
            if not os.path.exists(os.path.join(temp_dir, "kernel-metadata.json")):  # 获取本地内核信息
                print("kernel-metadata.json 文件不存在")
                continue
            local_kernel_queue.put_nowait({"name": i, "status": "no", "run_time": None})
    for i in range(6):  # 推送内核
        kn = local_kernel_queue.get_nowait()
        path = kernel_path + "/" + kn["name"]
        fully_name = ka.config_values[ka.CONFIG_NAME_USER] + "/" + kn["name"]
        try:
            res = ka.kernels_status(fully_name)  # 获取内核运行状态
            if res["status"] == "running":
                continue
        except ApiException as e:
            print(fully_name, e.status, e.reason)
            kernels_initialize(ka, kn["name"], path)  # 初始化
        ka.kernels_push(path)  # 提交文件夹中所有的内核
    local_kernel_queue.task_done()  # 消费任务完成
    schedule.enter(30 * 60 * 60, 0, local_push)  # 30小时后再次运行


def kernels_initialize(api, name, folder):
    """
    初始化kernel-metadata.json
    :param api: 实例对象
    :param name: 内核名，只能包含字母数字和-
    :param folder: 输出文件目录
    :return:
    """
    if not os.path.isdir(folder):
        raise ValueError('Invalid folder: ' + folder)
    meta_file = os.path.join(folder, api.KERNEL_METADATA_FILE)
    if os.path.exists(meta_file):  # 如果文件存在
        return meta_file

    username = api.get_config_value(api.CONFIG_NAME_USER)
    meta_data = {
        'id': username + '/' + name,  # 只能包含字母数字和-
        'title': name,
        'code_file': name + ".py",  # 只能包含字母数字和-
        'language': api.valid_push_language_types[0],  # python
        'kernel_type': api.valid_push_kernel_types[0],  # script
        'is_private': 'true',
        'enable_gpu': 'false',
        'enable_internet': 'true',
        'dataset_sources': [],
        'competition_sources': [],
        'kernel_sources': [],
    }
    with open(meta_file, 'w') as f:
        json.dump(meta_data, f, indent=2)

    return meta_file


if __name__ == '__main__':
    # download_kernels()
    # 注意 sched 模块不是循环的，一次调度被执行后就结束了，如果想再执行，请再次 enter
    # 四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, pull_push)  # 提交拉取的内核
    # schedule.enter(0, 0, local_push)  # 提交本地内核
    schedule.run()
