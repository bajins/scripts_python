#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Description: 
# @PreInstall: 
# @Author : claer
# @File : time_util.py
# @Version: 1.0.0
# @Time : 2019/9/25 18:49
# @Project: scripts_python
# @Package: 
# @Software: PyCharm
import datetime
import time


def get_every_day(begin_date, end_date):
    """
    获取两个日期间的所有日期
    :param begin_date:
    :param end_date:
    :return:
    """
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


def date_compare_to(begin_date, end_date):
    """
    比较两个日期大小
    :param begin_date:
    :param end_date:
    :return: 返回0为相等，1为begin比end大，-1为begin比end小
    """
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    if begin_date == end_date:
        return 0
    elif begin_date < end_date:
        return -1
    else:
        return 1


def time_compare_to(begin_time, end_time):
    """
    比较两个时间大小
    :param begin_time:
    :param end_time:
    :return: 返回0为相等，1为begin比end大，-1为begin比end小
    """
    begin_time = time.strftime("%Y-%m-%d-%H_%M_%S", begin_time)
    end_time = time.strftime("%Y-%m-%d-%H_%M_%S", end_time)
    if begin_time == end_time:
        return 0
    elif begin_time < end_time:
        return -1
    else:
        return 1
