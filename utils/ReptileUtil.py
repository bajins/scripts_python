#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Author : bajins www.bajins.com
# @File : ReptileUtil.py
# @Version: 1.0.0
# @Time : 2019/9/18 16:22
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm
"""
https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#id9
使用BeautifulSoup库爬取数据，
解析器有：html.parser、lxml、xml、html5lib
推荐使用lxml作为解析器，速度快，容错能力强，效率高
"""

import os
import platform
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions

from utils import HttpUtil, FileUtil, SystemUtil


def get_local_version(prefix):
    """
    获取本地chrome版本
    :param prefix:
    :return:
    """
    sysstr = platform.system()
    if sysstr == "Windows":
        local_version = SystemUtil.get_windows_software()["Google Chrome"].split(".")[0]
    elif sysstr == "Linux":
        local_version = os.popen('google-chrome --version').read().split(" ")[3].split(".")[0]

    for s in prefix:
        version = s.text
        if version.split(".")[0] == local_version:
            break

    return version


def download_chromedriver():
    """
    下载chrome驱动
    http://chromedriver.storage.googleapis.com/index.html
    :return:
    """
    # 获取版本号列表
    url = "http://chromedriver.storage.googleapis.com/"
    result = BeautifulSoup(HttpUtil.get(url, {"delimiter": "/", "prefix": ""}).text, features="lxml")
    prefix = result.find_all("prefix")
    # 过滤
    # info = [s.extract() for s in prefix('prefix')]

    local_version = get_local_version(prefix)

    # 获取版本下面的文件列表
    driver_list = BeautifulSoup(HttpUtil.get(url, {"delimiter": "/", "prefix": local_version}).text, features="lxml")
    filename_list = driver_list.find_all("key")

    for s in filename_list:
        s = s.text
        # 如果在文件名中找到系统平台名称
        if s.find(sys.platform) != -1:
            filename = s[len(local_version):]
            # 下载文件
            HttpUtil.download_file(url + s, None, filename)
            FileUtil.zip_extract(filename, None)


def download_taobao_chromedriver():
    """
    下载淘宝镜像chromedriver
    http://npm.taobao.org/mirrors/chromedriver
    :return:
    """
    # 获取版本号列表
    url = "http://npm.taobao.org/mirrors/chromedriver/"
    result = BeautifulSoup(HttpUtil.get(url).text, features="lxml")
    prefix = result.find("pre").find_all("a")
    # 过滤
    # info = [s.extract() for s in prefix('prefix')]

    local_version_url = url + get_local_version(prefix)

    # 获取版本下面的文件列表
    driver_list = BeautifulSoup(HttpUtil.get(local_version_url).text, features="lxml")
    filename_list = driver_list.find("pre").find_all("a")

    for s in filename_list:
        s = s.text
        # 如果在文件名中找到系统平台名称
        if s.find(sys.platform) != -1:
            # 下载文件
            HttpUtil.download_file(local_version_url + s, None, s)
            FileUtil.zip_extract(s, None)


def selenium_driver(url, debug=False):
    """
    获取驱动
    :param debug: 是否调试模式
    :param url:
    :return:
    """
    if sys.platform == "win32":
        path = "./chromedriver.exe"
    else:
        path = "./chromedriver"

    if not os.path.exists(path):
        download_taobao_chromedriver()

    # chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-agent={HttpUtil.USER_AGENT}')
    # 启动即窗口最大化
    options.add_argument("--start-maximized")

    if not debug:
        # 设置chrome浏览器无界面模式
        options.add_argument('--headless')
        # 谷歌文档提到需要加上这个属性来规避bug
        options.add_argument('--disable-gpu')
        # 隐身模式启动
        options.add_argument('-–incognito')
        # 取消沙盒模式
        options.add_argument('--no-sandbox')
        # 指定浏览器分辨率
        options.add_argument('window-size=1600x900')
        # 禁止加载所有插件，可以增加速度
        options.add_argument('-–disable-plugins')
        # 禁用扩展
        options.add_argument('--disable-extensions')
        # 隐藏滚动条, 应对一些特殊页面
        options.add_argument('--hide-scrollbars')
        # 这种方式在Headless的模式下是生效的， 非Headless模式下也是生效的。不加载图片, 提升速度
        # options.add_argument('blink-settings=imagesEnabled=false')
        options.add_argument('-–disable-images')
        # 手动指定使用的浏览器位置
        # options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        # 添加crx插件
        # options.add_extension('d:\crx\AdBlock_v2.17.crx')
        # 禁用JavaScript
        # options.add_argument("--disable-javascript")
        # 设置开发者模式启动，该模式下webdriver属性为正常值
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 用于定义下载不弹窗和默认下载地址（默认下载地址还要再后面的commands里启动，默认是不开启的）
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            'profile.default_content_settings.popups': 0,
            'download.default_directory': 'D:\\',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True,
            'profile.default_content_setting_values': {
                # 禁用浏览器弹窗
                'notifications': 2,
                "automatic_downloads": 0
            }
        }
        options.add_experimental_option('prefs', prefs)

    capa = DesiredCapabilities.CHROME
    # 懒加载模式，不等待页面加载完毕
    # capa["pageLoadStrategy"] = "none"

    # 打开浏览器,executable_path指定驱动位置
    driver = webdriver.Chrome(chrome_options=options, executable_path=path, desired_capabilities=capa)

    # 向Selenium Webwdriver添加对Chrome "send_command"的支持
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    # 禁用浏览器下载
    # https://github.com/TheBrainFamily/chimpy/issues/108#issuecomment-512836924
    # allow自动、deny禁止、default默认
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'deny', 'downloadPath': "D:\\"}}
    driver.execute("send_command", params)

    # 在启动浏览器并打开页面后，最大化浏览器
    # driver.maximize_window()
    # 在启动浏览器并打开页面后，最小化浏览器
    # driver.minimize_window()

    # 隐式等待是一个全局设置，设置后所有的元素定位都会等待给定的时间，
    # 直到元素出现为止，等待规定时间元素没出现就报错，秒为单位
    # driver.implicitly_wait(10)

    # 设置页面加载超时
    # driver.set_page_load_timeout(10)
    # 设置页面异步js执行超时
    # driver.set_script_timeout(10)

    # 打开网站
    driver.get(url)

    return driver


if __name__ == '__main__':
    # download_taobao_chromedriver()
    download_chromedriver()
