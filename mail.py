#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : mail.py
# @Version: 1.0.0
# @Time : 2019/9/12 15:20
# @Project: scripts_python
# @Package: 
# @Software: PyCharm
import json
import math
import random
import time

import constants
from utils import http_util, string_util
from utils.exception_util import MsgException


def short_time_mail_apply():
    """
    随机申请shorttimemail.com邮箱
    :return: 邮箱号
    """
    prefix = string_util.random_lowercase_alphanumeric(9)
    suffix = "@shorttimemail.com"
    data = {"prefix": prefix, "suffix": suffix}
    # post续期30分钟：/mail/continue
    # post销毁：/mail/destory
    # post删除邮件：/mail/delete ，参数：{ ids: ids.join('|') }以|分割字符串
    res = http_util.get_json(url=constants.SHORT_TIME_MAIL + "/mail/apply", data=data)
    if res.code != 200:
        raise MsgException(res.msg)
    return prefix + suffix


def short_time_mail_list(last_id):
    """
    查询邮件列表
    :param last_id:
    :return:
    """
    url = constants.SHORT_TIME_MAIL + "/mail/list"
    return http_util.get_json(url=url, data={"last_id": last_id})


def short_time_get_mail(id):
    """
    查询邮件内容
    :param last_id:
    :return:
    """
    url = constants.SHORT_TIME_MAIL + "/zh-Hans/mail/detail"
    return http_util.get_json(url=url, data={"id": id})


def lin_shi_you_xiang_suffix():
    """
    获取邮箱后缀
    :return:
    """
    suffix_array = ["@meantinc.com",
                    "@classesmail.com",
                    "@powerencry.com",
                    "@groupbuff.com",
                    "@figurescoin.com",
                    "@navientlogin.net",
                    "@programmingant.com",
                    "@castlebranchlogin.com",
                    "@bestsoundeffects.com",
                    "@vradportal.com",
                    "@a4papersize.net"]
    a = random.randint(0, 10)
    return suffix_array[a]


def lin_shi_you_xiang_apply(prefix):
    """
    获取邮箱
    :param prefix: 邮箱前缀
    :return:
    """
    url = constants.LIN_SHI_YOU_XIANG + "/api/v1/mailbox/keepalive"
    data = {"force_change": 1, "mailbox": prefix, "_ts": round(time.time() / 1000)}
    return http_util.get_json(url=url, data=data)


def lin_shi_you_xiang_list(prefix):
    """
    获取邮箱列表
    :param prefix: 邮箱前缀
    :return:
    """
    url = constants.LIN_SHI_YOU_XIANG + "/api/v1/mailbox/" + prefix
    return http_util.get_json(url=url, data=None)


def lin_shi_you_xiang_get_mail(prefix, id):
    url = constants.LIN_SHI_YOU_XIANG + "/mailbox/" + prefix + "/" + id + "/source"
    return http_util.get(url=url, data=None).text


def lin_shi_you_xiang_delete(prefix, id):
    """
    删除邮件delete请求
    :param id:  邮件编号
    :param prefix: 邮箱前缀
    :return:
    """
    url = constants.LIN_SHI_YOU_XIANG + "/api/v1/mailbox/" + prefix + "/" + id
    res = http_util.delete(url=url, data=None)
    res_json = json.loads(res.text)


if __name__ == '__main__':
    prefix = string_util.random_lowercase_alphanumeric(9)
    suffix = lin_shi_you_xiang_suffix()
    lin_shi_you_xiang_apply(prefix)
    lin_shi_you_xiang_list(prefix)
