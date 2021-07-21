#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Description: https://www.jianshu.com/p/e0f42bd3a3ea
# @PreInstall: 
# @Author : claer
# @File : multipart_file_util.py
# @Version: 1.0.0
# @Time : 2019/10/18 23:23
# @Project: scripts_python
# @Package: 
# @Software: PyCharm

import requests
import threading
import os
import time

from . import http_util


def download(url, file_name, headers=http_util.header):
    t = DownloadWorkerThread(url, file_name, headers=headers)
    t.start()
    return t


# 处理单个下载线程
class DownloadWorkerThread(threading.Thread):
    thread_count = 5
    file_lock = threading.Lock()
    file_info_lock = threading.Lock()

    def __init__(self, url, file_name, headers={}, thread_count=3):
        threading.Thread.__init__(self)
        self.content_length = self.get_content_length()
        self.range_manager = self.read_range_file()
        self.filename = file_name
        self.url = url
        self.file_info_name = file_name + ".tmp"
        self.headers = headers
        self.thread_count = thread_count

    def run(self):
        print(u"Begin Downloading \nurl= " + self.url + "\nfilename = " + self.filename)
        if self.url.strip() == "":
            return
        tlst = []
        for i in range(self.thread_count):
            t = threading.Thread(target=self.range_worker, args=(self,))
            print(u"Start Thread :" + t.getName())
            t.setDaemon(True)
            t.start()
            tlst.append(t)

        for t in tlst:
            t.join()

    def write_content(self, content, content_range):
        self.file_lock.acquire()
        with open(self.filename, 'rb+') as f:
            f.seek(content_range[0])
            f.write(content)
        self.file_lock.release()

        self.file_info_lock.acquire()
        self.range_manager.set_written_range(content_range)
        self.file_info_lock.release()

    def read_next_range(self):
        self.file_info_lock.acquire()
        time.sleep(0.1)
        r = self.range_manager.get_unwritten_range()
        self.file_info_lock.release()
        return r

    def read_range_file(self):
        self.file_info_lock.acquire()
        manager = None
        if os.path.exists(self.file_info_name):
            print("read filename ", self.file_info_name)
            manager = DownloadWorkerThread.FileInfoManager(self.file_info_name, url=self.url)
            self.content_length = manager.get_total_length()
            if self.url.strip() == "":
                self.url = manager.url_in_file
        else:

            print("create filename_info length:", str(self.content_length))
            with open(self.filename, "wb+") as f:
                f.seek(self.content_length)
            manager = DownloadWorkerThread.FileInfoManager(self.file_info_name, url=self.url,
                                                           filesize=self.content_length)
        self.file_info_lock.release()
        return manager

    def get_content_length(self):
        headers = self.headers
        headers['Range'] = "bytes=0-1"
        length = 0
        while length < 1024 * 1024 * 3:
            time.sleep(3)
            length = int(requests.get(self.url, headers=self.headers).headers['content-Range'].split('/')[1])
            print("Get length ", str(length))
        return length

    def range_worker(self, download_worker):
        while True:
            content_range = download_worker.read_next_range()
            if content_range == 0:
                os.remove(self.file_info_name)
                print(self.filename + " finished")
                break
            headers = download_worker.headers
            headers['Range'] = "bytes=" + str(content_range[0]) + "-" + str(content_range[1] - 1)
            while True:
                iTryTimes = 0
                r = requests.get(download_worker.url, headers=headers)
                if r.ok:
                    download_worker.write_content(r.content, content_range)
                    print("We are working on ", self.filename + " and now processing : ",
                          str(round(1.0 * content_range[1] / self.content_length * 100, 2)) + "% in size ",
                          str(round(self.content_length / 1024.0 / 1024.0, 2)) + "MB."
                          )
                    break
                else:
                    iTryTimes += 1
                    if iTryTimes > 1:
                        print("Downloading " + download_worker.url + " error. Now Exit Thread.")
                        return


def _concat(intervals, new_interval):
    if len(intervals) == 0:
        return [new_interval]
    response = [new_interval]
    for interval in intervals:
        i = response.pop()
        if interval[0] == interval[1]:
            continue
        if i[0] > interval[1]:
            response.append(interval)
            response.append(i)
        elif i[1] < interval[0]:
            response.append(i)
            response.append(interval)
        else:
            response.append((min(i[0], interval[0]), max(i[1], interval[1])))
    return response


class FileInfoManager:
    url_in_file = ""
    writing_range = []
    written_range = []
    unwritten_range = []

    def __init__(self, file_name, url="", file_size=0):
        self.filename = file_name
        if not os.path.exists(file_name):
            with open(file_name, "w") as f:
                f.write("unwritten_range=[(0," + str(file_size) + ")]\r\n")
                f.write("writing_range=[]\r\n")
                f.write("written_range=[]\r\n")
                f.write("url_in_file=" + url)
            self.unwritten_range.append((0, file_size))
            self.url_in_file = url
        else:
            with open(file_name, "r") as f:
                for l in f.readlines():
                    typ = l.split("=")[0]
                    if typ == "writing_range":
                        typ = "unwritten_range"
                    elif typ == "url_in_file":
                        if url.strip() == "":
                            self.url_in_file = l.split("=")[1]
                        else:
                            self.url_in_file = url
                        continue
                    for tup in l.split("=")[1][1:-3].split('),'):
                        if tup == "":
                            continue
                        if tup.find("(") != 0:
                            tup = tup[tup.find("("):]
                        if tup.find(")") != 0:
                            tup = tup[:tup.find(")")]
                        getattr(self, typ).append((int(tup.split(",")[0][1:]), int(tup.split(",")[1])))

    def get_total_length(self):
        if len(self.unwritten_range) > 0:
            return self.unwritten_range[-1][1]
        elif len(self.writing_range) > 0:
            return self.writing_range[-1][1]
        elif len(self.written_range) > 0:
            return self.written_range[-1][1]
        return 0

    def _save_to_file(self):
        with open(self.filename, "w") as f:
            f.write("writing_range=" + str(self.writing_range) + "\r\n")
            f.write("unwritten_range=" + str(self.unwritten_range) + "\r\n")
            f.write("written_range=" + str(self.written_range) + "\r\n")
            f.write("url_in_file=" + self.url_in_file)

    def _splice(self, intervals, new_interval):
        if len(intervals) == 0:
            return []
        intervals = _concat(intervals, (0, 0))
        response = []
        for interval in intervals:
            if interval[0] == interval[1]:
                continue
            if interval[0] > new_interval[1]:
                response.append(interval)
            elif interval[1] < new_interval[0]:
                response.append(interval)
            else:
                max_range = (min(interval[0], new_interval[0]), max(interval[1], new_interval[1]))
                if max_range != new_interval:
                    left = (min(max_range[0], new_interval[0]), max(max_range[0], new_interval[0]))
                    right = (min(max_range[1], new_interval[1]), max(max_range[1], new_interval[1]))
                    if left[0] != left[1]:
                        response.append(left)
                    if right[0] != right[1]:
                        response.append(right)
        return response

    def get_unwritten_range(self, size=1024 * 1024):
        if len(self.unwritten_range) == 0:
            return 0
        r = self.unwritten_range[0]
        r = (r[0], min(r[0] + size, r[1]))
        self.unwritten_range = self._splice(self.unwritten_range, r)
        self.writing_range = _concat(self.writing_range, r)
        self._save_to_file()
        return r

    def set_written_range(self, content_range):
        self.writing_range = self._splice(self.writing_range, content_range)
        self.written_range = _concat(self.written_range, content_range)
        self._save_to_file()
