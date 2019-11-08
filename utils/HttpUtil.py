#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : HttpUtil.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:32
# @Project: windows-wallpaper-python
# @Package:
# @Software: PyCharm


import json
import os
import shutil
import socket
import threading
import time
import urllib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import requests
import urllib3

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/72.0.3626.109 Safari/537.36 "
}

# 去除警告
requests.packages.urllib3.disable_warnings()
# 如果请求失败默认重试次数
requests.adapters.DEFAULT_RETRIES = 5


def get(url, data):
    """
    get请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    session = requests.sessions.Session()
    # 关闭多余的连接
    session.keep_alive = False
    return session.get(url=url, params=data, headers=headers, verify=False, timeout=600)


def post(url, data):
    """
    get请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    return requests.post(url=url, params=data, headers=headers, verify=False, timeout=600)


def delete(url, data):
    """
    delete请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    return requests.delete(url=url, params=data, headers=headers, verify=False, timeout=600)


def get_json(url, data):
    """
    get请求返回结果转json
    :param url:
    :param data:
    :return:
    """
    return json.loads(get(url=url, data=data).text)


def download_big_file(url, mkdir, name=""):
    """
    用requests下载大文件，边下边写
    :param url:
    :param mkdir:
    :param name:
    :return:
    """

    # 判断文件名称是否传入
    if name is None or name == "":
        ur = str(url).split("/")
        # 如果没传，就取URL中最后的文件名
        name = ur[len(ur) - 1]

    # 判断是否传入文件夹
    if mkdir is not None and mkdir != "":
        # 判断目录是否存在
        if not os.path.exists(mkdir):
            # 目录不存在则创建
            os.mkdir(mkdir)
        name = os.path.join(mkdir, name)

    start_time = time.time()
    with requests.get(url, stream=True, headers=headers, verify=False) as r:
        content_length = int(r.headers['content-length'])
        line = 'content-length: %dB/%.2fKB/%.2fMB'
        print(name, line % (content_length, content_length / 1024, content_length / 1024 / 1024))
        down_size = 0
        with open(name, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                down_size += len(chunk)
                line = '%d KB/s - %.2f MB，共 %.2f MB' % (down_size / 1024 / (time.time() - start_time),
                                                        down_size / 1024 / 1024, content_length / 1024 / 1024)
                print(name, line, end='\r')
                if down_size >= content_length:
                    break
        time_cost = time.time() - start_time
        print(name, '共耗时：%.2f s，平均速度：%.2f KB/s' % (time_cost, down_size / 1024 / time_cost))


def download_file(url, mkdir, name=""):
    """
    用requests下载文件，一次性读取到内存中然后写入
    :param url:
    :param mkdir:
    :param name:
    :return:
    """
    # detectionModule("requests")
    # 判断文件名称是否传入
    if name is None or name == "":
        ur = str(url).split("/")
        # 如果没传，就取URL中最后的文件名
        name = ur[len(ur) - 1]

    # 判断是否传入文件夹
    if mkdir is not None and mkdir != "":
        # 判断目录是否存在
        if not os.path.exists(mkdir):
            # 目录不存在则创建
            # os.mkdir(mkdir)
            os.makedirs(mkdir)
        name = os.path.join(mkdir, name)

    # 判断文件是否存在
    # if not os.path.exists(name):
    if not os.path.isfile(name):
        # 文件不存在才保存
        with open(name, "wb") as f:
            f.write(requests.get(url, headers=headers, verify=False, timeout=600).content)
    return name


def thread_download_file(url, mkdir, name=""):
    """
    启用单独线程下载文件
    :param url: 下载链接
    :param mkdir: 文件存放目录
    :param name: 文件名
    :return:
    """
    if url is None or url == "":
        raise ValueError("url参数不正确")
    if mkdir is None or mkdir == "":
        raise ValueError("mkdir文件目录参数不正确")

    # 启用单个线程下载
    threading.Thread(target=download_file, args=(url, mkdir, name)).start()


def thread_call_back(future):
    """
    线程回调执行
    :param future:
    :return:
    """
    print(future)
    print(future.result())


pool = ThreadPoolExecutor(max_workers=20)


def thread_pool_download_file(urls=[], mkdir=None):
    """
    启用线程池下载
    :param urls: 下载链接数组[{"url":"","filename":""}]
    :param mkdir: 文件存放目录
    :return:
    """
    if len(urls) == 0 or urls[0]["url"] == "":
        raise ValueError("url链接数组参数不正确")

    if mkdir is None or mkdir == "":
        raise ValueError("mkdir文件目录参数不正确")

    # thread_res = []

    for url in urls:
        # thread_res.append(pool.submit(download_file, url["url"], mkdir, urls["filename"]))
        pool.submit(download_file, url["url"], mkdir, urls["filename"]).add_done_callback(thread_call_back)


def download_file_move(url, mkdir, name, move_dir):
    """
    下载文件并移动到指定目录
    :param url: 文件链接
    :param mkdir: 文件保存目录
    :param name: 文件名
    :param move_dir: 移动到此目录
    :return:
    """
    filename = download_file(url, mkdir, name)

    if not os.path.exists(move_dir):
        # 目录不存在则创建
        os.mkdir(move_dir)

    if os.path.isfile(filename) and os.stat(filename).st_size > 102400:
        shutil.move(filename, os.path.join(move_dir, os.path.split(filename)[1]))


def download_file_list(urls, mkdir, name):
    """
    用urllib批量下载文件
    :param urls:
    :param mkdir:
    :param name:
    :return:
    """
    # 老版本去除警告方法
    # from requests.packages.urllib3.exceptions import InsecureRequestWarning
    # requests.packages.disable_warnings(InsecureRequestWarning)

    # 新版去除警告方法
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for url in urls:
        # 判断文件名称是否传入
        if name.strip() == '':
            ur = str(url).split("/")
            # 如果没传，就取URL中最后的文件名
            name = ur[len(ur) - 1]
        # 判断是否传入文件夹
        if mkdir.strip() != '':
            # 判断目录是否存在
            if not os.path.exists(mkdir):
                # 目录不存在则创建
                os.mkdir(mkdir)
            name = mkdir + name
        # os.path.join将多个路径组合后返回
        # LocalPath = os.path.join('C:/Users/goatbishop/Desktop',file)
        # 第一个参数url:需要下载的网络资源的URL地址
        # 第二个参数LocalPath:文件下载到本地后的路径
        urllib.request.urlretrieve(url, name)
        # response = urllib.request.urlopen(url)
        # pic = response.read()
        # with open(name, 'wb') as f:
        #     f.write(pic)


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_remote_ip(host_name):
    """
    获取指定域名IP地址
    :param host_name:域名
    :return:
    """
    try:
        return socket.gethostbyname(host_name)
    except BaseException as e:
        print(" %s:%s" % (host_name, e))
