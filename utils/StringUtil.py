#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : StringUtil.py
# @Version: 1.0.0
# @Time : 2019/8/22 9:10
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm
import json
import math
import random
import re
import string


def is_empty(obj):
    """
    判断数据是否为空
    :param obj:
    :return:
    """
    if isinstance(obj, str):
        if obj is None or len(obj) <= 0 or obj.strip() == '':
            return True
    elif isinstance(obj, set) or isinstance(obj, dict) or isinstance(obj, list):
        if obj is None or len(obj) <= 0 or bool(obj) or not any(obj):
            return True
    else:
        if obj or obj is None:
            return True
    return False


def not_empty(obj):
    """
    判断数据是否不为空
    :param obj:
    :return:
    """
    return not is_empty(obj)


def check_json(string):
    """
    确认是否为json
    :param string:
    :return:
    """
    try:
        json.loads(string)
        return True
    except BaseException as e:
        print(e)
        return False


def check_exist(string, substring):
    """
    判断字符串是否包含子串
    :param string:字符串
    :param substring: 子串
    :return:
    """
    string = string.lower()
    substring = substring.lower()
    # 使用正则表达式判断
    # if re.match("^.*" + substring + ".*", string):
    if string.find(substring) != -1 and substring in string:
        return True
    else:
        return False


def check_startswith(string, substring):
    """
    判断字符串是以什么开头
    :param string:字符串
    :param substring:需要判断的开头字符串
    :return:
    """
    # 检查你输入的是否是字符类型
    if isinstance(string, str):
        raise ValueError("参数不是字符串类型")
    # 判断字符串以什么开头
    if string.startswith(substring):
        return True

    return False


def check_endswith(string, substring):
    """
    判断字符串是以什么结尾
    :param string:字符串
    :param substring:需要判断的结尾字符串
    :return:
    """
    # 检查你输入的是否是字符类型
    if isinstance(string, str):
        raise ValueError("参数不是字符串类型")
    # 判断字符串以什么结尾
    if string.endswith(substring):
        return True

    return False


def random_lowercase_alphanumeric(length, charset="abcdefghijklmnopqrstuvwxyz0123456789_"):
    """
    生成一个指定长度的小写字母、数字、下划线的字符串
    :param length:
    :param charset:
    :return:
    """
    rd = ""
    for i in range(length):
        random_poz = math.floor(random.random() * len(charset))
        rd += charset[random_poz:random_poz + 1]
    return rd


def random_string(length=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(length)]
    return ''.join(str_list)


def hump_case_underline_lower(text):
    """
    驼峰(hump/camel)转下划线小写，已考虑到连续大写，不拆分数字
    :param text: 驼峰形式字符串
    :return: 字母全小写的下划线形式字符串
    """
    lists = text[0]
    for i in range(1, len(text)):
        if text[i].isupper() and (not text[i - 1].isupper() or (text[i - 1].isupper() and text[i + 1].islower())):
            # 加'_',当前为大写，前一个字母为小写
            lists += '_'
            lists += text[i]
        else:
            lists += text[i]
    return lists.lower()


def hump2underline(hump_str):
    """
    驼峰形式字符串转成下划线形式，已考虑到连续大写，拆分数字
    :param hump_str: 驼峰形式字符串
    :return: 字母全小写并拆分数字的下划线形式字符串
    """
    # 第一个参数匹配正则，匹配小写字母和大写字母的分界位置
    # 第二个参数使用了正则分组的后向引用
    hump_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', hump_str)
    # 匹配字母与数字分界位置
    hump_str = re.sub('(.)([0-9]+)', r'\1_\2', hump_str)
    # 匹配小写字母数字与大写字母分界位置
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', hump_str).lower()


def underline2hump(underline_str):
    """
    下划线形式字符串转成驼峰形式
    :param underline_str: 下划线形式字符串
    :return: 驼峰形式字符串
    """
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    return re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)


def json_hump2underline(hump_json_str):
    """
    把一个json字符串中的所有字段名都从驼峰形式替换成下划线形式。
    注意：因为考虑到json可能具有多层嵌套的复杂结构，所以这里直接采用正则文本替换的方式进行处理，而不是采用把json转成字典再进行处理的方式
    :param hump_json_str: 字段名为驼峰形式的json字符串
    :return: 字段名为下划线形式的json字符串
    """
    # 从json字符串中匹配字段名的正则
    # 注：这里的字段名只考虑由英文字母、数字、下划线组成
    attr_ptn = re.compile(r'"\s*(\w+)\s*"\s*:')
    # 使用hump2underline函数作为re.sub函数第二个参数的回调函数
    return re.sub(attr_ptn, lambda x: '"' + hump2underline(x.group(1)) + '" :', hump_json_str)
