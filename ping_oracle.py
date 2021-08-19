#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : https://www.bajins.com
# @Description : 获取Oracle云各个区域的延迟
# @File : ping_oracle.py
# @Version: 1.1.0
# @Time : 2020/7/26 11:00
# @Project: scripts_python
# @Package:
# @Software: PyCharm
from collections import namedtuple
from pythonping import ping
from prettytable import PrettyTable

lists = [
    {"region": "亚太地区", "list": [
        {"area": "日本东部 东京", "addr": "objectstorage.ap-tokyo-1.oraclecloud.com"},
        {"area": "日本中部 大阪", "addr": "objectstorage.ap-osaka-1.oraclecloud.com"},
        {"area": "韩国中部 首尔", "addr": "objectstorage.ap-seoul-1.oraclecloud.com"},
        {"area": "韩国北部 春川", "addr": "objectstorage.ap-chuncheon-1.oraclecloud.com"},
        {"area": "澳大利亚东部 悉尼", "addr": "objectstorage.ap-sydney-1.oraclecloud.com"},
        {"area": "澳大利亚东南部 墨尔本", "addr": "objectstorage.ap-melbourne-1.oraclecloud.com"},
        {"area": "印度西部 孟买", "addr": "objectstorage.ap-mumbai-1.oraclecloud.com"},
        {"area": "印度南部 海得拉巴", "addr": "objectstorage.ap-hyderabad-1.oraclecloud.com"}
    ]
     },
    {"region": "北美地区", "list": [
        {"area": "美国东部 阿什本", "addr": "objectstorage.us-ashburn-1.oraclecloud.com"},
        {"area": "美国西部 凤凰城", "addr": "objectstorage.us-phoenix-1.oraclecloud.com"},
        {"area": "美国西部 圣何塞", "addr": "objectstorage.us-sanjose-1.oraclecloud.com"},
        {"area": "加拿大东南部 蒙特利尔", "addr": "objectstorage.ca-montreal-1.oraclecloud.com"},
        {"area": "加拿大东南部 多伦多", "addr": "objectstorage.ca-toronto-1.oraclecloud.com"}
    ]
     },
    {"region": "欧洲地区", "list": [
        {"area": "英国南部 伦敦", "addr": "objectstorage.uk-london-1.oraclecloud.com"},
        {"area": "英国西部 加的夫", "addr": "objectstorage.uk-cardiff-1.oraclecloud.com"},
        {"area": "德国中部 法兰克福", "addr": "objectstorage.eu-frankfurt-1.oraclecloud.com"},
        {"area": "瑞士北部 苏黎世", "addr": "objectstorage.eu-zurich-1.oraclecloud.com"},
        {"area": "荷兰西北部 阿姆斯特丹", "addr": "objectstorage.eu-amsterdam-1.oraclecloud.com"}
    ]
     },
    {"region": "中东地区", "list": [
        {"area": "阿联酋东部 迪拜", "addr": "objectstorage.me-dubai-1.oraclecloud.com"},
        {"area": "沙特阿拉伯西部 吉达", "addr": "objectstorage.me-jeddah-1.oraclecloud.com"}
    ]
     },
    {"region": "南美地区", "list": [
        {"area": "巴西东部 圣保罗", "addr": "objectstorage.sa-saopaulo-1.oraclecloud.com"},
        {"area": "智利中部 圣地亚哥", "addr": "objectstorage.sa-santiago-1.oraclecloud.com"}
    ]
     }
]


def ping_check(addr):
    from tcping import Ping
    ping = Ping(addr)
    ping.ping(10)

    ret = ping.result.rows
    for r in ret:
        print(r)

    ret = ping.result.raw
    print(ret)

    ret = ping.result.table
    print(ret)


x = PrettyTable()

Statistics = namedtuple('Statistics', ["地域", "地区", "Host", "Minimum", "Average", "Maximum"])
x.field_names = Statistics._fields

for ls in lists:
    region = ls.get("region")
    for ds in ls.get("list"):
        area = ds.get("area")
        addr = ds.get("addr")
        try:
            res = ping(addr, count=10, verbose=False, out=None)
            x.add_row(Statistics(region, area, addr, res.rtt_min_ms, res.rtt_avg_ms, res.rtt_max_ms))
        except:
            x.add_row(Statistics(region, area, addr, 0, 0, 0))

        # ping_check(addr)

# x.align = "l"
x.padding_width = 5
print(x.get_string(sortby="Average", reversesort=False))
