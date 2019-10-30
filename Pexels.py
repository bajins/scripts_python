#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Pexels.py
# @Version: 1.0.0
# @Time : 2019/10/16 15:22
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm
import os
import time, sched
from threading import Timer

import psutil
import zhconv
from bs4 import BeautifulSoup

import Constants
from utils import ReptileUtil, HttpUtil, ThreadPool, DatabaseUtil

save_dir = "images"

s3 = DatabaseUtil.Sqlite3(os.path.join(Constants.DATA_PATH, "pexels"))

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


def download_latest_images(page, directory):
    html = ReptileUtil.bs("https://www.pexels.com/zh-cn/new-photos?page=" + str(page), None)
    articles = html.find_all("article")
    pages_html = html.find("div", {"class": "pagination"})

    for article in articles:
        # 图片id
        image_id = article["data-photo-modal-medium-id"]
        # 图片原始大小
        # image_org_size = article["data-photo-modal-download-value-original"]
        # 图片下载链接
        download_url = article["data-photo-modal-image-download-link"]
        image_name = "pexels-photo-" + image_id + ".jpg"

        info_html = ReptileUtil.bs("https://www.pexels.com/zh-cn/photo/" + image_id, None)
        tags = info_html.find("meta", {"name": "keywords"}).attrs["content"].replace(" ", "").replace("'", "")
        if len(tags) > 0 and tags != "":
            # 简繁转换
            tags = zhconv.convert(tags[:len(tags) - 7], 'zh-cn')

        # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('href')).attrs["href"]
        # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('data-url')).attrs["data-url"]

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
    if len(pages_html) > 0 and psutil.virtual_memory().percent < 80 and run_count <= 8:
        pages_html = BeautifulSoup(str(pages_html), features="lxml").find_all("a")
        page_total = pages_html[len(pages_html) - 2].text
        # 如果不是最后一页，那么就继续下载下一页
        if page != page_total:
            download_latest_images(page + 1, directory)

    elif len(pages_html) == 0:
        run_count = 0
        Timer(400, download_latest_images, (page, directory)).start()
    else:
        run_count = 0
        Timer(400, download_latest_images, (page + 1, directory)).start()


if __name__ == '__main__':
    res = DatabaseUtil.select(s3.connect(), select_table)
    if len(res) == 0:
        row = DatabaseUtil.insert(s3.connect(), crate_sql)

    res = DatabaseUtil.select(s3.connect(), "SELECT page from images where type='latest' order by id desc limit 1")
    if len(res) == 0:
        res = 1
    else:
        res = res[0][0]

    download_latest_images(int(res), save_dir)
