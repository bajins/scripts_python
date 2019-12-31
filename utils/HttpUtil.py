#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : HttpUtil.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:32
# @Project: windows-wallpaper-python
# @Package:
# @Software: PyCharm
import asyncio
import io
import json
import os
import socket
import time
import urllib

import aiofiles
import aiohttp
import requests
import urllib3

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/77.0.3865.75 Safari/537.36 "

# 去除警告
requests.packages.urllib3.disable_warnings()
# 如果请求失败默认重试次数
requests.adapters.DEFAULT_RETRIES = 5


def get(url, data=None):
    """
    get请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    session = requests.sessions.Session()
    # 关闭多余的连接
    session.keep_alive = False
    return session.get(url, params=data, headers={"User-Agent": USER_AGENT}, verify=False, timeout=600)


def post(url, data):
    """
    get请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    return requests.post(url, data, headers={"User-Agent": USER_AGENT}, verify=False, timeout=600)


def delete(url, data):
    """
    delete请求
    :param url:请求地址
    :param data:数据，map或dict格式
    :return:
    """
    return requests.delete(url=url, params=data, headers={"User-Agent": USER_AGENT}, verify=False, timeout=600)


def get_json(url, data):
    """
    get请求返回结果转json
    :param url:
    :param data:
    :return:
    """
    return json.loads(get(url=url, data=data).text)


def download_big_file_urlib(url, mkdir, name=""):
    """
    使用urlib下载大文件和小文件都差不多，
    只不过在read（）函数中指定了每次读入文件的大小
    不能使用迭代器，只能使用for循环，还得判断最后文件是否读完
    :param url:
    :param mkdir:
    :param name:
    :return:
    """
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

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

    req = Request(url)
    # 增加header头信息
    req.add_header('User-Agent', USER_AGENT)

    response = urlopen(req)
    while True:
        # 在read（）中指定读入块的大小
        tmp = response.read(8196)
        if not tmp:
            break
    response.close()
    with open(name, 'wb') as f:
        f.write(tmp)


def download_big_file(url, mkdir, name=""):
    """
    用requests下载大文件，边下边写
    当把get函数的stream参数设置成True时，它不会立即开始下载，
    当你使用iter_content或iter_lines遍历内容或访问内容属性时才开始下载。
    需要注意一点：文件没有下载之前，它也需要保持连接。

    iter_content：一块一块的遍历要下载的内容
    iter_lines：一行一行的遍历要下载的内容
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
    req = requests.get(url, stream=True, headers={"User-Agent": USER_AGENT}, verify=False)
    with req as r:
        content_length = int(r.headers['content-length'])
        print(name, 'content-length: %dB/%.2fKB/%.2fMB' % (
            content_length, content_length / 1024, content_length / 1024 / 1024))
        down_size = 0
        with open(name, 'wb') as f:
            for chunk in r.iter_content(8196):
                if chunk:
                    f.write(chunk)
                down_size += len(chunk)
                print(name, '%d KB/s - %.2f MB，共 %.2f MB' % (
                    down_size / 1024 / (time.time() - start_time), down_size / 1024 / 1024,
                    content_length / 1024 / 1024), end='\r')
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
        reqs = requests.get(url, headers={"User-Agent": USER_AGENT}, verify=False, timeout=600)
        with reqs as req:
            with open(name, "wb") as f:
                f.write(req.content)
    return name


def save_file(fd: io.BufferedWriter, chunk):
    fd.write(chunk)


async def download_one_fetch_async(url: str, mkdir: str, name: str):
    """
    异步分块下载一个文件
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
            # os.mkdir(mkdir)
            os.makedirs(mkdir)
        name = os.path.join(mkdir, name)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(name, 'wb') as f:
                while 1:
                    chunk = await resp.content.read(8196)
                    if not chunk:
                        break
                    # f.write(chunk)
                    lp = asyncio.get_event_loop()
                    # None事件循环中包含一个默认的线程池(ThreadPoolExecutor)
                    lp.run_in_executor(None, save_file, f, chunk)


async def download_one_async(url, mkdir, name):
    """
    异步下载一个文件
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
            # os.mkdir(mkdir)
            os.makedirs(mkdir)
        name = os.path.join(mkdir, name)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async with aiofiles.open(name, 'wb') as f:
                await f.write(await response.read())


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
