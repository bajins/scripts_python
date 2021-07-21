#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : translation_util.py
# @Version: 1.0.0
# @Time : 2019/10/22 9:20
# @Project: scripts_python
# @Package: 
# @Software: PyCharm

import requests
from googletrans import Translator


def translate_youdao(content):
    """
    有道翻译
    :param content:
    :return:
    """
    content = content.strip()
    if content == '' or len(content) == 0:
        raise ValueError("要翻译的内容不能为空")
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
    data = {}
    data['i'] = content
    data['from'] = 'AUTO'
    data['to'] = 'AUTO'
    data['smartresult'] = 'dict'
    data['client'] = 'fanyideskweb'
    data['salt'] = '1538295833420'
    data['sign'] = '07'
    data['doctype'] = 'json'
    data['version'] = '2.1'
    data['keyfrom'] = 'fanyi.web'
    data['action'] = 'FY_BY_REALTIME'
    data['typoResult'] = 'false'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/67.0.3396.99 Safari/537.36'
    }
    result = requests.post(url, data, headers=headers)
    trans = result.json()
    return trans['translateResult'][0][0]['src']


def translate_google(content):
    """
    Google翻译
    :param content:
    :return:
    """
    content = content.strip()
    if content == '' or len(content) == 0:
        raise ValueError("要翻译的内容不能为空")
    if len(content) > 4891:
        raise ValueError("翻译的长度超过限制")
        # 使用方法
    translator = Translator(service_urls=['translate.google.cn'])
    return translator.translate(content, src='en', dest='zh-cn').text
