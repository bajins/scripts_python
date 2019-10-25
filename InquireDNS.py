#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : InquireDNS.py
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

import Constants
from utils import HttpUtil, FileUtil, StringUtil, ObjectUtil, ReptileUtil


def get_chinaz_ip():
    """
    通过chinaz查询dns
    :return:
    """
    for domain in Constants.GITHUB_DOMAIN:
        try:
            soup = ReptileUtil.selenium_bs(Constants.CHINAZ_DNS, "w360", domain)
            lis = soup.find_all("li", class_="ReLists")
            if lis is not None:
                for li in lis:
                    ip = li.find(class_="w60-0").string
                    if not ip == "-" and ip is not None:
                        addr = li.find(class_="w23-0").string
                        ttl = li.find(class_="w14-0").string
                        print(addr, ip, ttl, domain)
        except Exception as e:
            print(e)


def delete_dns(dns):
    """
    删除数组中的dns
    :param dns: 数组
    :return: 删除后的hosts
    """
    hosts = FileUtil.read_file(Constants.HOSTS_PATH)
    new_hosts = []
    for host in hosts:
        if not ObjectUtil.is_in_array(host.strip("\n"), dns):
            new_hosts.append(host)
    return new_hosts


def update_hosts(new_hosts):
    """
    更新覆写hosts
    :param new_hosts: 新的dns数组
    :return:
    """
    FileUtil.remove_read_only(Constants.HOSTS_PATH)
    FileUtil.write_lines(Constants.HOSTS_PATH, new_hosts)
    # 刷新dns
    os.system("ipconfig /flushdns")


def get_myssl_ip():
    """
    通过myssl查询dns
    :return:
    """

    new_hosts = delete_dns(Constants.GITHUB_DOMAIN)

    for domain in Constants.GITHUB_DOMAIN:
        try:
            data = {"qtype": 1, "host": domain, "qmode": -1}
            response = HttpUtil.get(url=Constants.MYSSL_DNS, data=data)
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
    new_hosts = delete_dns(Constants.GITHUB_DOMAIN)

    for domain in Constants.GITHUB_DOMAIN:
        try:
            data = {"server": "8.8.8.8", "rrtype": "A", "domain": domain}
            response = HttpUtil.get(url=Constants.SHORT_TIME_MAIL_DNS, data=data)
            jsp = json.loads(response.text)
            if jsp["code"] == 0:
                # 拼接host
                for us in jsp["data"]:
                    new_hosts.append(us["value"] + " " + domain + "\n")
        except Exception as e:
            print("错误：", e)

    update_hosts(new_hosts)
