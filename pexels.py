#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : pexels.py
# @Version: 1.0.0
# @Time : 2019/10/16 15:22
# @Project: scripts_python
# @Package: 
# @Software: PyCharm
import asyncio
import os
import re
import threading
import time

import zhconv
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import constants
from utils import http_util, database_util, file_util, system_util, translation_util, reptile_util
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

s3 = database_util.Sqlite3(os.path.join(constants.DATA_PATH, "pexels"))

run_count = 0


def download_latest_images(page, directory):
    try:
        system_util.restart_process(os.path.abspath(__file__))

        html = BeautifulSoup(http_util.get("https://www.pexels.com/zh-cn/new-photos?page=" + str(page)).text,
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

            info_html = BeautifulSoup(http_util.get("https://www.pexels.com/zh-cn/photo/" + image_id).text,
                                      features="lxml")
            tags = info_html.find("meta", {"name": "keywords"}).attrs["content"]
            if len(tags) > 0 and tags != "":
                # 简繁转换
                tags = zhconv.convert(tags[:len(tags) - 7], 'zh-cn')
                tags = re.sub(r"[^a-z,\u4e00-\u9fa5]+|^,|,$", "", tags).replace(",,", ",")
            s3.execute_commit(f"""
            INSERT OR IGNORE INTO images(image_id,suffix,url,type,page,tags) 
            VALUES('{image_id}','{download_url[download_url.rfind(".") + 1:]}',
            '{download_url}','latest','{page}','{tags}')
            """)
            # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('href')).attrs["href"]
            # dl = info_html.find(lambda tag: tag.has_attr('data-id') and tag.has_attr('data-url')).attrs["data-url"]

            # 判断文件是否存在
            if not os.path.exists(os.path.join(directory, image_name)):
                # 每张图片启用单个线程下载
                # done = ThreadPool.pool.submit(HttpUtil.download_file, download_url, directory, image_name)
                # done.add_done_callback(ThreadPool.thread_call_back)
                asyncio.run(http_util.download_one_async(download_url, directory, image_name))

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

    except Exception as e:
        print(e)
    finally:
        print("当前活跃线程数:", threading.activeCount())
        time.sleep(400)
        download_latest_images(page, directory)


def download_latest_images_selenium(page, directory):
    """
    使用selenium获取
    :param page:
    :param directory:
    :return:
    """
    system_util.restart_process(os.path.abspath(__file__))
    driver = reptile_util.selenium_driver("https://www.pexels.com/new-photos?page=" + str(page))
    try:
        articles = driver.find_elements_by_tag_name("article")
        next_page = True
        try:
            driver.find_element_by_xpath("/html/body/section/div[4]/div/a[@rel='next']")
        except Exception as e:
            next_page = False
        # 获取当前所有窗口句柄（窗口A、B）
        main_window = driver.current_window_handle
        print(articles)
        for article in articles:
            # 图片id
            image_id = article.get_attribute("data-photo-modal-medium-id")
            info_url = "https://www.pexels.com/photo/" + image_id
            # 通过执行js打开新标签页并访问url
            driver.execute_script(f"window.open('{info_url}')")
            driver.switch_to.window(driver.window_handles[-1])
            tags = ""
            if driver.title.find("500") == -1:
                tags = driver.find_element_by_xpath("//meta[@name='keywords']").get_attribute("content")
                tags = translation_util.translate_google(tags).replace("，", ",")
                tags = re.sub(r"[^a-z,\u4e00-\u9fa5]+|^,|,$", "", tags).replace(",,", ",")
            # 关闭当前窗口。
            driver.close()
            # 关闭新选项卡后回到主窗口，必须做这一步，否则会引发错误
            driver.switch_to.window(main_window)
            # 图片下载链接
            download_url = f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg?dl={image_id}.jpg"
            s3.execute_commit(f"""
            INSERT OR IGNORE INTO images(image_id,suffix,url,type,page,tags) 
            VALUES('{image_id}','jpg','{download_url}','latest','{page}','{tags}')
            """)
            image_name = f"pexels-photo-{image_id}.jpg"
            # 判断文件是否存在
            if not os.path.exists(os.path.join(directory, image_name)):
                asyncio.run(http_util.download_one_async(download_url, directory, image_name))
        global run_count
        run_count += 1

        # 如果获取到的页数大于0不是最后一页
        if next_page and run_count <= 10:
            download_latest_images(page + 1, directory)
        else:
            if next_page:
                page += 1
            else:
                page = 1
            run_count = 0

    except Exception as e:
        print(e)
    finally:
        # 关闭当前窗口。
        driver.close()
        # 关闭浏览器并关闭chreomedriver进程
        driver.quit()
        print("当前活跃线程数:", threading.activeCount())
        time.sleep(400)
        download_latest_images(page, directory)


def run_command(directory):
    dir_size = file_util.count_dir_size(directory)
    if dir_size >= 107374182400:
        print(file_util.size_unit_format(dir_size))
        print(os.system("rclone move /home/reptile-python/images/ gdrive:/images --min-size 100k"))
        print(file_util.size_unit_format(file_util.count_dir_size(directory)))
    print(os.popen("rclone dedupe gdrive:/images --dedupe-mode newest").read())
    print(os.popen("rclone delete gdrive:/images --max-size 100k").read())
    threading.Timer(21600, run_command, (directory,)).start()


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

    # threading.Thread(target=run_command, args=("images",)).start()

    # download_latest_images(int(res), "images")
    download_latest_images_selenium(int(res), "images")
