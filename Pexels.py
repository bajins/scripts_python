#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Pexels.py
# @Version: 1.0.0
# @Time : 2019/10/16 15:22
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm
import gc
import os
import threading
import time

import psutil
import zhconv
from bs4 import BeautifulSoup

import Constants
from utils import ReptileUtil, HttpUtil, ThreadPool, DatabaseUtil, FileUtil

s3 = DatabaseUtil.Sqlite3(os.path.join(Constants.DATA_PATH, "pexels"))

run_count = 0


def download_latest_images(page, directory):
    try:
        dir_size = FileUtil.count_dir_size(directory)
        if dir_size >= 1073741824:
            print(FileUtil.size_unit_format(dir_size))
            # raise IOError("存储的图片超过1GB")
            print(os.system("rclone move /home/reptile-python/images/ gdrive:/images --min-size 100k"))
            print(FileUtil.size_unit_format(FileUtil.count_dir_size(directory)))

        wait()

        html = BeautifulSoup(HttpUtil.get("https://www.pexels.com/zh-cn/new-photos?page=" + str(page)).text,
                             features="lxml")
        articles = html.find_all("article")
        pages_html = BeautifulSoup(str(html.find("div", {"class": "pagination"})), features="lxml").find_all("a")
        page_total = int(pages_html[len(pages_html) - 2].text)

        print(page, len(articles), page_total)
        if page > page_total:
            page = 1
            raise ValueError("page超出范围")

        for article in articles:
            # 图片id
            image_id = article["data-photo-modal-medium-id"]
            # 图片原始大小
            # image_org_size = article["data-photo-modal-download-value-original"]
            # 图片下载链接
            download_url = article["data-photo-modal-image-download-link"]
            image_name = f"pexels-photo-{image_id}.jpg"

            info_html = BeautifulSoup(HttpUtil.get("https://www.pexels.com/zh-cn/photo/" + image_id).text,
                                      features="lxml")
            tags = info_html.find("meta", {"name": "keywords"}).attrs["content"].replace(" ", "").replace("'", "")
            if len(tags) > 0 and tags != "":
                # 简繁转换
                tags = zhconv.convert(tags[:len(tags) - 7], 'zh-cn')

            s3.execute_commit(f"""
            INSERT OR IGNORE INTO images(image_id,suffix,url,type,page,tags) 
            VALUES('{image_id}','{download_url[download_url.rfind(".") + 1:]}','{download_url}','latest','{page}','{tags}')
            """)
            # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('href')).attrs["href"]
            # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('data-url')).attrs["data-url"]

            # 判断文件是否存在
            if not os.path.exists(os.path.join(directory, image_name)):
                # 每张图片启用单个线程下载
                done = ThreadPool.pool.submit(HttpUtil.download_file, download_url, directory, image_name)
                # done.add_done_callback(ThreadPool.thread_call_back)
                # threading.Timer(30, HttpUtil.download_file, (download_url, directory, image_name))

        global run_count
        run_count += 1

        # 如果获取到的页数大于0不是最后一页
        if page_total > 0 and page <= page_total and run_count <= 10:
            download_latest_images(page + 1, directory)
        else:
            if len(pages_html) > 0 and page <= page_total:
                page += 1
            if page > page_total:
                page = 1
            run_count = 0

    finally:
        print("当前活跃线程数:", threading.activeCount())
        time.sleep(400)
        download_latest_images(page, directory)


def wait():
    if psutil.virtual_memory().percent >= 80:
        print('内存使用：', psutil.Process(os.getpid()).memory_info().rss)
        print("当前内存占用率：", psutil.virtual_memory().percent)
        print("垃圾回收机制是否打开:", gc.isenabled())
        # 释放内存
        gc.collect()
    if psutil.virtual_memory().percent >= 80:
        wait()


def run_command():
    print(os.popen("rclone dedupe gdrive:/images --dedupe-mode newest").read())
    print(os.popen("rclone delete gdrive:/images --max-size 100k").read())
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
    res = s3.select("SELECT page from images where type='latest' order by id desc limit 1")
    if len(res) == 0:
        res = 1
    else:
        res = res[0][0]

    download_latest_images(int(res), "images")
    run_command()
