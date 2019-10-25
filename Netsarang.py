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
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import Mail
from utils import HttpUtil, StringUtil, ReptileUtil, TimeUtil
from utils.ExceptionUtil import MsgException


def send_mail(mail, product):
    """
    根据产品和邮箱让Netsarang发送邮件
    :param mail:    邮箱
    :param product: 产品
    :return:
    """
    if product == "xshell":
        url = "https://www.netsarang.com/zh/xshell-download"

    if product == "xftp":
        url = "https://www.netsarang.com/zh/xftp-download"

    if product == "xmanager-power-suite":
        url = "https://www.netsarang.com/zh/xmanager-power-suite-download"

    if product == "xshell-plus":
        url = "https://www.netsarang.com/zh/xshell-plus-download"

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


netsarang_info = {}


def download(product):
    """
    获取下载链接地址
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

    send_mail(mail, product)

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
    href = ReptileUtil.selenium_attribute(href, "a[target='download_frame']", "href")

    href = href.replace(".exe", "r.exe")

    # 把产品信息存储到变量
    netsarang_info[product] = [datetime.now(), href]

    return href


if __name__ == '__main__':
    print(download("xshell"))
