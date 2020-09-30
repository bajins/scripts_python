#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : 360.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:47
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm

# 获取分类
import logging
import os

import Constants
from utils import HttpUtil
from utils.ExceptionUtil import MsgException


def get_360_category():
    data = {'c': 'WallPaper', 'a': 'getAllCategoriesV2', 'from': '360chrome'}
    category = HttpUtil.get(url='http://wallpaper.apc.360.cn/index.php', data=data)
    if category["errno"] != "0":
        raise MsgException('请求接口错误', category["errmsg"])
    return category["data"]


# 获取分类下的图片
def get_360_category_image():
    category = get_360_category()
    logging.debug(category)
    # cid分类ID，start从第几幅图开始(用于分页)，count每次加载的数量最大200
    data = {'c': 'WallPaper', 'a': 'getAppsByCategory', 'cid': '36', 'start': 0, 'count': 200, 'from': '360chrome'}
    response = HttpUtil.get(url='http://wallpaper.apc.360.cn/index.php', data=data)
    if response["errno"] != "0":
        raise MsgException('请求接口错误', response["errmsg"])

    images = response["data"]
    get_360_image(images)
    logging.debug(images)


# 获取最近更新的壁纸
def get_360_update_image():
    # order排序，start从第几幅图开始(用于分页)，count每次加载的数量最大200
    data = {'c': 'WallPaper', 'a': 'getAppsByOrder', 'order': 'create_time', 'start': 0, 'count': 200,
            'from': '360chrome'}
    response = HttpUtil.get(url='http://wallpaper.apc.360.cn/index.php', data=data)
    if response["errno"] != "0":
        raise MsgException('请求接口错误', response["errmsg"])

    images = response["data"]
    get_360_image(images)


# 获取图片
def get_360_image(images):
    for image in images:
        url = image["url"]
        # 拼接目录路径
        directory = os.path.join(Constants.APP_DIRECTORY, "images")
        # 如果目录不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)

        urls = url.split("/")
        # 拼接文件绝对路径
        image_path = os.path.join(directory, urls[len(urls) - 1])

        HttpUtil.download_file(image_path, url)
