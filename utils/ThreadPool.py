#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : ThreadPool.py
# @Version: 1.0.0
# @Time : 2019/10/17 11:45
# @Project: scripts_python
# @Package: 
# @Software: PyCharm

import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED, as_completed
import multiprocessing

# IO密集型：线程数 = CPU核心数/(1-阻塞系数)
# Blocking Coefficient(阻塞系数)（一般为0.8~0.9之间） = 阻塞时间/(阻塞时间+使用CPU的时间)
# 计算密集型：线程数 = CPU内核线程数*2（CPU有超线程），线程数 = CPU核数+1（CPU无超线程）
pool = ThreadPoolExecutor(max_workers=int(multiprocessing.cpu_count() / (1 - 0.9)))

thread_results = []


def thread_call_back(future):
    """
    线程回调执行
    :param future:
    :return:
    """
    # print(future)
    # print(future.result())
    tr_l = len(thread_results)
    # 当前线程完成，从线程池移除
    thread_results.pop(0)
    print("线程数组大小：", tr_l, "->", len(thread_results))


def can_thread(name):
    """
    线程池判断
    :param name:
    :return:
    """
    # 如果线程池满
    if len(thread_results) >= 50:
        # 休眠5秒
        time.sleep(5)

    # 如果休眠后线程池还是满的
    if len(thread_results) >= 50:
        # 继续调用当前函数处理
        can_thread(name)

    if len(thread_results) < 50:
        # 只有线程池小于最大线程数才调用线程
        thread_results.append(name)
