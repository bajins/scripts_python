#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Wallhaven.py
# @Version: 1.0.0
# @Time : 2019/10/12 10:27
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm
import os
import time
from threading import Timer

import psutil

import Constants
from utils import ReptileUtil, HttpUtil, ThreadPool, DatabaseUtil, TranslationUtil

save_dir = "images"

s3 = DatabaseUtil.Sqlite3(os.path.join(Constants.DATA_PATH, "wallhaven"))

# 查询表
select_table = "select name from sqlite_master where type='table' and name='images'"

# 获取自增的主键值：SELECT last_insert_rowid()
crate_sql = """
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
    )
    """

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
        html = ReptileUtil.bs(url + str(page), None)
        figure = html.find_all("figure")
        # 获取所有包含指定属性的标签
        page_all = html.find_all(lambda tag: tag.has_attr('original-title'))

        for label in figure:
            image_id = label.attrs["data-wallpaper-id"]

            # 图片详情页
            info_html = ReptileUtil.bs("https://wallhaven.cc/w/" + image_id, None)
            tags_html = info_html.find_all("a", {"class": "tagname", "rel": "tag"})
            # 图片的标签
            tags = ",".join([tag_html.text for tag_html in tags_html]).replace("'", "")
            if len(tags) > 0 and tags != "":
                tags = TranslationUtil.translate_google(tags).replace("，", ",")

            download_url = info_html.find("img", {"id": "wallpaper"}).attrs["src"]
            if len(download_url) <= 0 and download_url == "":
                raise ConnectionError("获取下载链接失败")

            image_name = download_url.split("/")
            image_name = image_name[len(image_name) - 1]
            # 判断文件是否存在
            # if not os.path.exists(name):
            if not os.path.isfile(os.path.join(directory, image_name)):
                # 每张图片启用单个线程下载
                done = ThreadPool.pool.submit(HttpUtil.download_file, download_url, directory, image_name)
                # done.add_done_callback(ThreadPool.thread_call_back)

            suffix = download_url[len(download_url) - 3:]

            insert_sql = f"""
            INSERT OR IGNORE INTO images(image_id,suffix,url,type,page,tags) 
            VALUES('{image_id}','{suffix}','{download_url}','latest','{page}','{tags}')
            """
            DatabaseUtil.insert(s3.connect(), insert_sql)

        global run_count
        run_count += 1

        # 如果获取到的页数大于0，并且内存占用率小于80%时
        if len(page_all) > 0 and psutil.virtual_memory().percent < 80 and run_count <= 8:
            page_total = page_all[len(page_all) - 1].text
            # 如果不是最后一页，那么就继续下载下一页
            if page != page_total:
                download_images(url, page + 1, directory)

        elif len(page_all) == 0:
            run_count = 0
            Timer(400, download_images, (url, page, directory)).start()
        else:
            run_count = 0
            Timer(400, download_images, (url, page + 1, directory)).start()

    except Exception as e:
        print(e)
        Timer(400, download_images, (url, page, directory)).start()


def download_tag_images(tag_id, page, directory):
    """
    根据标签下载文件
    :param tag_id: 标签id
    :param page: 页数
    :param directory: 文件保存的目录
    :return:
    """
    url = "https://wallhaven.cc/search?q=" + tag_id + "&page="
    download_images(url, page, directory)


def download_latest_images(page, directory):
    """
    下载最新文件
    :param page: 页数
    :param directory: 文件保存的目录
    :return:
    """
    url = "https://wallhaven.cc/latest?page="
    download_images(url, page, directory)


def get_tag(page):
    """
    获取标签
    :param page: 页码
    :return:
    """
    html = ReptileUtil.bs("https://wallhaven.cc/tags?page=" + str(page), None)
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


if __name__ == '__main__':
    res = DatabaseUtil.select(s3.connect(), select_table)
    if len(res) == 0:
        row = DatabaseUtil.insert(s3.connect(), crate_sql)

    # get_tag(1)
    # download_tag_images("id%3A222", 3, "images")

    res = DatabaseUtil.select(s3.connect(), "SELECT page from images where type='latest' order by id desc limit 1")
    if len(res) == 0:
        res = 1
    else:
        res = res[0][0]
    download_latest_images(int(res), save_dir)
