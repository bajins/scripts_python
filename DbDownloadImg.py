#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : DbDownloadImg.py
# @Version: 1.0.0
# @Time : 2019/8/27 10:25
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm

# global适用于函数内部修改全局变量的值
# nonlocal关键字用来在函数或其他作用域中使用外层(非全局)变量
# 如果不使用关键字，对全局变量或者外部变量进行修改，python会默认将全局变量隐藏起来

import os
import sys
import argparse
import datetime
import configparser

import Constants
from utils import DatabaseUtil, HttpUtil, FileUtil

print("==============================================================")
# if len(sys.argv) < 6:
#     # print("请输入参数！")
#     quit()

print("执行脚本名：", sys.argv[0])
print(":::::::::::::::执行开始时间：" +
      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "::::::::::::::")

# 初始化配置
config = FileUtil.Config(Constants.APP_CONF)

host = config.get("MYSQL", "HOST")
port = config.get("MYSQL", "PORT")
user = config.get("MYSQL", "USER")
password = config.get("MYSQL", "PASSWORD")
database = config.get("MYSQL", "BD_NAME")
charset = config.get("MYSQL", "CHARSET")
table = "test"
tableLimitStart = 10
tableLimitEnd = 20
# 将path转换成规范的文件路径
fileMkdir = os.path.normpath("images") + os.sep
sqlite3Database = fileMkdir + database

# 判断目录是否存在
if not os.path.exists(fileMkdir):
    # 目录不存在则创建
    os.mkdir(fileMkdir)

# 拆分驱动器和文件路径，并以元组返回结果；主要针对win有效，Linux元组第一个总是空。
# print(os.path.splitdrive(fileMkdir))

# 判断返回path的目录路径，就是os.path.split(path)的第一个元素。是否存在，如果存在返回True
# if not os.path.exists(os.path.dirname(fileMkdir)):
#     print("请确认填写的路径盘符是否正确！！！")
#     sys.exit(0)


image = []
s3 = DatabaseUtil.Sqlite3(sqlite3Database)
mysql = DatabaseUtil.Mysql(host, port, user, password, database, charset)


def run():
    # download_file_fist(result,fileMkdir,"")

    # print(result)
    # for d in result:
    #     if d == "path":
    #         continue
    try:
        global image
        image = DatabaseUtil.select(s3.connect(), "SELECT id, db_id from " + table + " order by id desc limit 1")
        if len(image) > 0:
            print("查询到Sqlite3数据库表中最大ID：", image[len(image) - 1][0])
            global tableLimitStart
            tableLimitStart = image[len(image) - 1][0]
    except Exception as e:
        print("没有查询到数据库表：", e)
        crate_sql = "CREATE TABLE " + table + " (id INTEGER PRIMARY KEY NOT NULL,db_id TEXT NOT NULL)"
        DatabaseUtil.insert(s3.connect(), crate_sql)

    # 查询出MySQL中的数据
    result = DatabaseUtil.select_limit(mysql.connect(), table, tableLimitStart, tableLimitEnd)
    if len(result) <= 0:
        print("没有查询到MySQL数据库数据")
        sys.exit(0)

    # 创建锁
    # lock = threading.RLock()
    # # 锁定
    # lock.acquire()
    # # 释放锁
    # lock.release()

    # 定义Sqlite3表ID
    i = 0
    if len(image) > 0:
        i = tableLimitStart
    # 循环所有数据
    for d in result:
        image_id = str(d[0])
        url = str(d[3])

        # 每张图片启用单个线程下载
        HttpUtil.thread_download_file(url, fileMkdir, "")

        i = i + 1
        # image = selectSqlite3BD(database, "SELECT id, db_id from "+table+" where id='" + str(i) + "'")
        # if len(image) <= 0:
        #  OR IGNORE 防止插入重复数据
        insert_sql = "INSERT OR IGNORE INTO " + table + " (id,db_id) VALUES (" + str(i) + "," + image_id + ")"
        DatabaseUtil.insert(s3.connect(), insert_sql)

    image = DatabaseUtil.select(s3.connect(), "SELECT count(*) from " + table)
    print("执行完成后最终数据库数据条数：", image[0][0])
    print("最终文件个数：", len([name for name in os.listdir(fileMkdir) if os.path.isfile(os.path.join(fileMkdir, name))]))

    print(":::::::::::::::执行完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "::::::::::::::")


if __name__ == "__main__":
    run()
