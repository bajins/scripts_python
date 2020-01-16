#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Netsarang.py
# @Version: 1.0.0
# @Time : 2019/9/17 18:22
# @Project: tool-gui-python
# @Package: 
# @Software: PyCharm


import base64
import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import Mail
from utils import HttpUtil, StringUtil, ReptileUtil, TimeUtil
from utils.ExceptionUtil import MsgException

netsarang_info = {}


def send_mail_dp(mail: str, product: str):
    """
    通过ChromeDP发送邮件
    :param mail:    邮箱
    :param product: 产品
    :return:
    """
    if product == "xshell":
        url = "https://www.netsarang.com/zh/xshell-download"
    elif product == "xftp":
        url = "https://www.netsarang.com/zh/xftp-download"
    elif product == "xlpd":
        url = "https://www.netsarang.com/zh/Xlpd"
    elif product == "xmanager":
        url = "https://www.netsarang.com/zh/xmanager-download"
    elif product == "xshellplus":
        url = "https://www.netsarang.com/zh/xshell-plus-download"
    elif product == "powersuite":
        url = "https://www.netsarang.com/zh/xmanager-power-suite-download"

    try:
        driver = ReptileUtil.selenium_driver(url)
        # 使用selenium通过id，name或class的方式来获取到这个input标签
        # 查找元素，传入值（输入的内容）
        driver.find_element_by_css_selector("input[name='user-name']").send_keys(mail.split("@")[0])
        driver.find_element_by_css_selector("input[name='email']").send_keys(mail)

        # 提交
        driver.find_element_by_css_selector('input[value="开始试用"][type="submit"]').click()

        # 显式等待设置一个等待时间，直到这个元素出现就停止等待，如果没出现就抛出异常
        WebDriverWait(driver, 60).until(expected_conditions.title_contains(u"Thank You – 下载 – NetSarang Website"))

        # 获取网页源代码
        # innerText，textContent，innerHTML
        html = driver.find_element_by_css_selector(".fusion-text h1").text

        if "感谢您提交的下载我们软件的请求" not in html:
            raise MsgException("邮件发送失败！")

    finally:
        # 关闭当前窗口。
        driver.close()
        # 关闭浏览器并关闭chreomedriver进程
        driver.quit()


def get_url_dp(product):
    """
    通过ChromeDP获取下载产品信息
    :param product: 产品
    :return:
    """
    if product == "" or product is None:
        raise MsgException("产品不能为空")

    if netsarang_info is not None and netsarang_info and product in netsarang_info.keys():
        info = netsarang_info[product]
        # 如果数据不为空，并且日期为今天，这么做是为了避免消耗过多的性能，每天只查询一次
        if len(info) > 1 and not info and TimeUtil.date_compare_to(info[0], datetime.now()) == 0:
            return info[1]

    prefix = StringUtil.random_lowercase_alphanumeric(9)
    suffix = Mail.lin_shi_you_xiang_suffix()

    Mail.lin_shi_you_xiang_apply(prefix)
    mail = prefix + suffix

    send_mail_dp(mail, product)

    time.sleep(10)

    mail_list = Mail.lin_shi_you_xiang_list(prefix)

    mail_len = len(mail_list)
    if mail_len == 0 or not mail_list:
        raise MsgException("邮件列表为空！")

    mailbox = mail_list[mail_len - 1]["mailbox"]
    if mailbox is None or mailbox == "":
        raise MsgException("邮件列表为空！")

    mail_id = mail_list[mail_len - 1]["id"]
    if mail_id is None or mail_id == "":
        raise MsgException("邮件ID为空！")

    # 获取最新一封邮件
    mail_content = Mail.lin_shi_you_xiang_get_mail(mailbox, mail_id)

    # 解密，邮件协议Content-Transfer-Encoding指定了base64
    html_text = base64.b64decode(mail_content.split("AmazonSES")[1])
    # 解析解密后的HTML
    html = BeautifulSoup(html_text, features="html.parser")
    # 查找带token的标签的值
    href = html.find("a", {"target": "_blank"}).text

    # 请求token链接地址获取下载链接
    # bs = ReptileUtil.selenium_bs(href)
    # href = bs.find("a", {"target": "download_frame"})["href"]

    try:
        driver = ReptileUtil.selenium_driver(href)
        driver.implicitly_wait(10)
        href = driver.find_element_by_css_selector("a[target='download_frame']").get_attribute("href")
    finally:
        # 关闭当前窗口。
        driver.close()
        # 关闭浏览器并关闭chreomedriver进程
        driver.quit()
    href = href.replace(".exe", "r.exe")

    # 把产品信息存储到变量
    netsarang_info[product] = [datetime.now(), href]

    return href


def send_mail(mail: str, product: str):
    """
    使用requests发送邮件
    :param mail:
    :param product:
    :return:
    """
    product_code = ""
    product_name = ""
    if product == "xshell":
        product_code = "4203"
        product_name = "xshell-download"
    elif product == "xftp":
        product_code = "4242"
        product_name = "xftp-download"
    elif product == "xlpd":
        product_code = "4280"
        product_name = "xlpd-download"
    elif product == "xmanager":
        product_code = "4162"
        product_name = "xmanager-download"
    elif product == "xshellplus":
        product_code = "4132"
        product_name = "xshell-plus-download"
    elif product == "powersuite":
        product_code = "4066"
        product_name = "xmanager-power-suite-download"

    if product_code == "" or product_name == "":
        raise MsgException("产品不匹配")

    data = {
        "_wpcf7": (None, "3016"),
        "_wpcf7_version": (None, "5.1.1"),
        "_wpcf7_locale": (None, "en_US"),
        "_wpcf7_unit_tag": (None, f"wpcf7-f3016-p{product_code}-o2"),
        "_wpcf7_container_post": (None, product_code),
        "g-recaptcha-response": (None, ""),
        "md": (None, "setDownload"),
        "language": (None, "3"),
        "downloadType": (None, "0"),
        "licenseType": (None, "0"),
        "action": (None, "/json/download/process.html"),
        "user-name": (None, mail),
        "email": (None, mail),
        "company": (None, ""),
        "product_name": (None, product_name),
    }
    res = requests.post("https://www.netsarang.com/json/download/process.html", data,
                        headers={"User-Agent": HttpUtil.USER_AGENT}, verify=False, timeout=600)
    res = json.load(res.text)
    if not res or res["errorCounter"] != 0 or not res["result"]:
        raise MsgException("邮箱发送失败！")


def get_url(lang: str, token: str):
    """
    使用requests获取url
    :param lang:
    :param token:
    :return:
    """
    language = "2"
    if lang == 'en':
        language = '2'
    if lang == 'ko':
        language = '1'
    if lang == 'zh':
        language = '3'
    if lang == 'ru':
        language = '8'
    if lang == 'pt':
        language = '9'
    data = {
        'md': (None, 'checkDownload'),
        'token': (None, token),
        'language': (None, language)
    }
    res = requests.post("https://www.netsarang.com/json/download/process.html", data,
                        headers={"User-Agent": HttpUtil.USER_AGENT}, verify=False, timeout=600)
    return json.load(res.text)


if __name__ == '__main__':
    print(get_url_dp("xshell"))
