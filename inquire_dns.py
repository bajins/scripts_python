#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : inquire_dns.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:56
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm


import fileinput
import json
import os
import re
import shutil
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import constants
from utils import http_util, file_util, string_util, object_util, reptile_util


def get_chinaz_ip():
    """
    通过chinaz查询dns
    :return:
    """
    try:
        for domain in constants.GITHUB_DOMAIN:
            try:
                driver = reptile_util.selenium_driver(constants.CHINAZ_DNS)
                # driver.set_page_load_timeout(20)
                input_element = driver.find_element_by_xpath('//*[@id="host"]')
                # 传入值，输入的内容
                input_element.send_keys(domain)
                # 提交
                input_element.submit()
                # driver.set_script_timeout(60)
                # https://zhuanlan.zhihu.com/p/61536685
                # WebDriverWait(driver, 120).until(expected_conditions.presence_of_element_located(
                #     (By.XPATH, "//*[@class='ReListCent ReLists bor-b1s clearfix']")))
                lis = driver.find_elements_by_xpath("//*[@class='ReListCent ReLists bor-b1s clearfix']")
                for li in lis:
                    if not li.text == "":
                        li_split = li.text.split("\n")
                        print(li_split[1], li_split[3])
            except Exception as e:
                print(e)
    finally:
        # 关闭当前窗口。
        driver.close()
        # 关闭浏览器并关闭chreomedriver进程
        driver.quit()


def delete_dns(dns):
    """
    删除数组中的dns
    :param dns: 数组
    :return: 删除后的hosts
    """
    hosts = file_util.read_file(constants.HOSTS_PATH)
    new_hosts = []
    for host in hosts:
        if not object_util.is_in_array(host.strip("\n"), dns):
            new_hosts.append(host)
    return new_hosts


def update_hosts(new_hosts):
    """
    更新覆写hosts
    :param new_hosts: 新的dns数组
    :return:
    """
    file_util.remove_read_only(constants.HOSTS_PATH)
    file_util.write_lines(constants.HOSTS_PATH, new_hosts)
    # 刷新dns
    os.system("ipconfig /flushdns")


def get_myssl_ip():
    """
    通过myssl查询dns
    :return:
    """

    new_hosts = delete_dns(constants.GITHUB_DOMAIN)

    for domain in constants.GITHUB_DOMAIN:
        try:
            data = {"qtype": 1, "host": domain, "qmode": -1}
            response = http_util.get(url=constants.MYSSL_DNS, data=data)
            jsp = json.loads(response.text)
            if jsp["code"] == 0 and jsp["error"] is None:
                result_data = jsp["data"]
                addr_us = result_data["01"][0]["answer"]["records"]
                # addr_hk = result_data["852"][0]["answer"]["records"]
                # addr_cn = result_data["86"][0]["answer"]["records"]

                # 拼接host
                for us in addr_us:
                    new_hosts.append(us["value"] + " " + domain + "\n")
        except Exception as e:
            print("错误：", e)

    update_hosts(new_hosts)


def get_short_time_mail_dns():
    """
    通过shorttimemail.com查询DNS
    :return:
    """
    new_hosts = delete_dns(constants.GITHUB_DOMAIN)

    for domain in constants.GITHUB_DOMAIN:
        try:
            data = {"server": "8.8.8.8", "rrtype": "A", "domain": domain}
            response = http_util.get(url=constants.SHORT_TIME_MAIL_DNS, data=data)
            jsp = json.loads(response.text)
            if jsp["code"] == 0:
                # 拼接host
                for us in jsp["data"]:
                    new_hosts.append(us["value"] + " " + domain + "\n")
        except Exception as e:
            print("错误：", e)

    update_hosts(new_hosts)
