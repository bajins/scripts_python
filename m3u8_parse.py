#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description: 根据m3u8描述文件下载文件
# https://www.bajins.com/Shell/Python%E7%88%AC%E8%99%AB.html#m3u8%E8%A7%A3%E6%9E%90%E4%B8%8B%E8%BD%BD%E8%A7%A3%E5%AF%86%E5%90%88%E5%B9%B6
# @PreInstall: pycryptodome
# @Author : https://www.bajins.com
# @File : m3u8_parse.py
# @Version: 1.0.0
# @Time : 2020/1/11 22:09
# @Project: reptile-python
# @Package: 
# @Software: PyCharm

import os
import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import m3u8
import requests
from glob import iglob

from natsort import natsorted
from concurrent.futures import ThreadPoolExecutor
# pip3 uninstall Crypto 并删除 Lib/site-packages/crypto
# pip3 install pycryptodome
from Crypto.Cipher import AES

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 " \
             "Safari/537.36"


# https://docs.python.org/zh-cn/3/library/dataclasses.html
@dataclass
class DownLoadM3U8(object):
    m3u8_url: str
    file_name: str

    def __post_init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        if not self.file_name:
            self.file_name = re.sub(r".*/|\..*", "", m3u8_url) + ".mp4"
        self.m3u8_obj = m3u8.load(self.m3u8_url)
        self.cryptor = self.get_key()

    def get_key(self):
        """
        获取key进行解密，这里可以获取method加密方式进行解密
        """
        if self.m3u8_obj.keys and self.m3u8_obj.keys[0]:
            res = requests.get(self.m3u8_obj.keys[0].absolute_uri, headers={'User-Agent': USER_AGENT})
            # AES 解密
            return AES.new(res.content, AES.MODE_CBC, res.content)
        else:
            return None

    def get_ts_url(self):
        for seg in self.m3u8_obj.segments:
            yield urljoin(self.m3u8_obj.base_uri, seg.uri)

    def download_ts(self, url_info):
        """
        下载ts文件，写入时如果有加密需要解密
        """
        url, ts_name = url_info
        res = requests.get(url, headers={'User-Agent': USER_AGENT})
        with open(ts_name, 'wb') as fp:
            if self.cryptor is not None:
                fp.write(self.cryptor.decrypt(res.content))
            else:
                fp.write(res.content)

    def download_all_ts(self):
        ts_urls = self.get_ts_url()
        for index, ts_url in enumerate(ts_urls):
            self.thread_pool.submit(self.download_ts, [ts_url, f'{index}.ts'])
        # 此方式可能使视频合并时顺序错乱
        # for file in self.m3u8_obj.files:
        #     url = urljoin(self.m3u8_obj.base_uri, file)
        #     self.thread_pool.submit(self.download_ts, [url, url[url.rfind("/") + 1:]])
        self.thread_pool.shutdown()

    def run(self):
        # 如果是第一层M3U8文件，那么就获取第二层的url
        if self.m3u8_obj.playlists and self.m3u8_obj.data.get("playlists"):
            self.m3u8_url = urljoin(self.m3u8_obj.base_uri, self.m3u8_obj.data.get("playlists")[0]["uri"])
            self.__post_init__()
        if not self.m3u8_obj.segments or not self.m3u8_obj.files:
            raise ValueError("m3u8数据不正确，请检查")
        self.download_all_ts()
        ts_path = '*.ts'
        with open(self.file_name, 'wb') as fn:
            for ts in natsorted(iglob(ts_path)):
                with open(ts, 'rb') as ft:
                    sc_line = ft.read()
                    fn.write(sc_line)
        [os.remove(ts) for ts in iglob(ts_path)]
        if os.path.exists("key.key"):
            os.remove("key.key")


if __name__ == '__main__':
    # aHR0cHM6Ly93d3cuMTAyNHV1LmNjL3ZvZC9saXN0aW5nLTQtMC0wLTAtMC0wLTAtMC0wLTEuaHRtbA==
    # m3u8_url = 'https://zk.wb699.com/2019/03/06/aLdpUIBeHC48HGTk/playlist.m3u8'
    m3u8_url = 'https://cdn.jwplayer.com/manifests/alBw0754.m3u8'
    file_name = ''

    start = time.time()

    M3U8 = DownLoadM3U8(m3u8_url, file_name)
    M3U8.run()

    end = time.time()
    print('耗时:', end - start)
