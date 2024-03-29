#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : bing.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:47
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm
import logging
import os
import time

import constants
from utils import http_util, file_util


def get_bing():
    """
    获取必应图片地址
    :return:
    """
    data = {'format': 'js', 'idx': 0, 'n': 1}
    try:
        response = http_util.get_json(url='http://cn.bing.com/HPImageArchive.aspx', data=data)
        logging.debug(response)
    except Exception as e:
        logging.error("网络请求错误：", e)
        time.sleep(120)
        get_bing()
    images = response["images"]
    url = "http://cn.bing.com" + images[0]["url"].split("&")[0]

    # 拼接目录路径
    directory = os.path.join(constants.APP_DIRECTORY, "images")

    image_name = url.split("=")[1]
    # 拼接文件绝对路径
    image_path = os.path.join(directory, image_name)
    # 下载图片
    http_util.download_file(url, directory, image_name)
    # 分割文件名和后缀，如果后缀不为bmp
    if os.path.splitext(image_name)[1] != "bmp":
        # 转为bmp
        image_path = file_util.image_to_bmp(image_path)
