#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Wallhaven.py
# @Version: 1.0.0
# @Time : 2019/10/12 10:27
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm
import gc
import os
import platform
import threading
import time

import psutil
from bs4 import BeautifulSoup

import Constants
from utils import ReptileUtil, HttpUtil, ThreadPool, DatabaseUtil, TranslationUtil, FileUtil

s3 = DatabaseUtil.Sqlite3(os.path.join(Constants.DATA_PATH, "wallhaven"))

run_count = 0


def download_images(url, page, directory):
    """
    下载图片
    :param url: 链接
    :param page: 页
    :param directory: 文件存放目录
    :return:
    """
    try:
        dir_size = FileUtil.count_dir_size(directory)
        if dir_size >= 1073741824:
            print(FileUtil.size_unit_format(dir_size))
            # raise IOError("存储的图片超过1GB")
            print(os.system("rclone move /home/reptile-python/images/ onedrive:/images --min-size 100k"))
            print(FileUtil.size_unit_format(FileUtil.count_dir_size(directory)))

        wait()

        html = BeautifulSoup(HttpUtil.get(url + str(2472)).text, features="lxml")
        figure = html.find_all("figure")
        # 获取所有包含指定属性的标签
        page_all = html.find_all(lambda tag: tag.has_attr('original-title'))
        page_total = int(page_all[len(page_all) - 1].text)

        print(page, len(figure), page_total)
        if page > page_total:
            page = 1
            raise ValueError("page超出范围")

        for label in figure:
            image_id = label.attrs["data-wallpaper-id"]

            # 图片详情页
            info_html = BeautifulSoup(HttpUtil.get("https://wallhaven.cc/w/" + image_id).text, features="lxml")
            tags_html = info_html.find_all("a", {"class": "tagname", "rel": "tag"})
            # 图片的标签
            tags = ",".join([tag_html.text for tag_html in tags_html]).replace("'", "")
            if len(tags) > 0 and tags != "":
                tags = TranslationUtil.translate_google(tags).replace("，", ",")

            download_url = info_html.find("img", {"id": "wallpaper"}).attrs["src"]
            if len(download_url) <= 0 or download_url == "":
                raise ConnectionError("获取下载链接失败")

            s3.execute_commit(f"""
            INSERT OR IGNORE INTO images(image_id,suffix,url,type,page,tags) 
            VALUES('{image_id}','{download_url[download_url.rfind(".") + 1:]}','{download_url}','latest','{page}','{tags}')
            """)

            image_name = download_url.split("/")
            image_name = image_name[len(image_name) - 1]
            # 判断文件是否存在
            # if not os.path.exists(name):
            if not os.path.isfile(os.path.join(directory, image_name)):
                # 每张图片启用单个线程下载
                done = ThreadPool.pool.submit(HttpUtil.download_file, download_url, directory, image_name)
                # done.add_done_callback(ThreadPool.thread_call_back)
                # threading.Timer(30, HttpUtil.download_file, (download_url, directory, image_name))

        global run_count
        run_count += 1

        # 如果获取到的页数大于0不是最后一页，并且内存占用率小于80%时
        if len(page_all) > 0 and page <= page_total and run_count <= 10:
            download_images(url, page + 1, directory)
        else:
            if len(page_all) > 0:
                page += 1
            if page > page_total:
                page = 1
            run_count = 0

    finally:
        print("当前活跃线程数:", threading.activeCount())
        time.sleep(400)
        download_images(url, page, directory)


def download_tag_images(tag_id, page, directory):
    """
    根据标签下载文件
    :param tag_id: 标签id
    :param page: 页数
    :param directory: 文件保存的目录
    :return:
    """
    download_images(f"https://wallhaven.cc/search?q={tag_id}&page=", page, directory)


def download_latest_images(page, directory):
    """
    下载最新文件
    :param page: 页数
    :param directory: 文件保存的目录
    :return:
    """
    download_images("https://wallhaven.cc/latest?page=", page, directory)


def get_tag(page):
    """
    获取标签
    :param page: 页码
    :return:
    """
    html = BeautifulSoup(HttpUtil.get(f"https://wallhaven.cc/tags?page={str(page)}").text, features="lxml")
    tags_html = html.find_all("a", {"class": "sfw"})
    for tag_html in tags_html:
        url = tag_html.attrs["href"]
        tag_id = url[url.rfind("/") + 1:]
        tag_text = tag_html.text
        print(tag_id, tag_text)

    # 获取所有包含指定属性的标签
    page_all = html.find_all(lambda tag: tag.has_attr('original-title'))
    page_total = page_all[len(page_all) - 1].text
    # 如果不是最后一页，那么就继续下载下一页
    if page != page_total:
        get_tag(page + 1)


def wait():
    """
    垃圾回收
    :return:
    """
    if psutil.virtual_memory().percent >= 80:
        print('内存使用：', psutil.Process(os.getpid()).memory_info().rss)
        print("当前内存占用率：", psutil.virtual_memory().percent)
        print("垃圾回收机制是否打开:", gc.isenabled())
        # 释放内存
        gc.collect()
    if psutil.virtual_memory().percent >= 80:
        wait()


def run_command():
    print(os.popen("rclone dedupe onedrive:/images --dedupe-mode newest").read())
    print(os.popen("rclone delete onedrive:/images --max-size 100k").read())
    threading.Timer(86400, run_command).start()


if __name__ == '__main__':
    if not s3.is_table_exist("images"):
        # 获取自增的主键值：SELECT last_insert_rowid()
        s3.execute_commit("""
            CREATE TABLE images (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                image_id TEXT NOT NULL,
                suffix TEXT NOT NULL,
                url TEXT NOT NULL,
                type TEXT,
                page TEXT,
                tags TEXT,
                create_time TEXT DEFAULT (DATETIME('NOW', 'LOCALTIME')),
                modify_time TEXT
            )""")
    # get_tag(1)
    # download_tag_images("id%3A222", 3, "images")
    res = s3.select("SELECT page from images where type='latest' order by id desc limit 1")
    if len(res) == 0:
        res = 1
    else:
        res = res[0][0]
    download_latest_images(int(res), "images")
    run_command()
