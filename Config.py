#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : Config.py
# @Version: 1.0.0
# @Time : 2019/8/27 10:28
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm

import os

from utils import FileUtil


def generate_conf():
    """
    如果配置文件不存在，则生成
    :return:
    """
    conf = os.path.join(os.getcwd(), "app.conf")
    if not os.path.exists(conf):
        content = "# 全局配置\n"
        content += "[APP]\n"
        content += "# 数据存放目录\n"
        content += "DATA_DIR = \n"
        content += "# 使用哪种数据库：MySQL或者Sqlite3\n"
        content += "DATABASE = \n"
        content += "# MySQL配置\n"
        content += "[MYSQL]\n"
        content += "# 地址\n"
        content += "HOST = \n"
        content += "# 端口\n"
        content += "PORT = \n"
        content += "# 用户名\n"
        content += "USER = \n"
        content += "# 密码\n"
        content += "PASSWORD = \n"
        content += "# 数据库名称\n"
        content += "BD_NAME = \n"
        content += "# 字符编码\n"
        content += "CHARSET = \n"
        content += "# Sqlite3配置\n"
        content += "[SQLITE3]\n"
        content += "# 数据库名称\n"
        content += "BD_NAME = \n"
        content += "# 字符编码\n"
        content += "CHARSET = \n"
        FileUtil.writ_file(conf, content)


def init():
    """
    初始化
    :return:
    """
    app = FileUtil.Config("app.conf")
    data_dir = app.get("APP", "DATA_DIR")
    if data_dir == "" or data_dir is None:
        raise ValueError("请配置数据存放目录！")

    # 如果目录不存在
    if not os.path.exists(data_dir):
        # 父级目录
        parent_path = os.path.dirname(os.path.dirname(__file__))
        # 拼接目录
        data_dir = os.path.join(parent_path, data_dir)
        # 创建目录
        os.mkdir(data_dir)

    database = app.get("APP", "DATABASE")
    if database == "" or database is None or (database.lower() != "mysql" and database.lower() != "sqlite3"):
        raise ValueError("请配置使用的数据库！")
    if database.lower() == "mysql":
        database = database.upper()
        host = app.get(database, "HOST")
        if host == "" or host is None:
            raise ValueError("请配置MySQL数据库地址！")
        port = app.get(database, "PORT")
        if port == "" or port is None:
            raise ValueError("请配置MySQL数据库端口！")
        user = app.get(database, "USER")
        if user == "" or user is None:
            raise ValueError("请配置MySQL数据库用户名！")
        password = app.get(database, "PASSWORD")
        if password == "" or password is None:
            raise ValueError("请配置MySQL数据库密码！")
        db_name = app.get(database, "BD_NAME")
        if db_name == "" or db_name is None:
            raise ValueError("请配置MySQL数据库名称！")
        charset = app.get(database, "CHARSET")
        if charset == "" or charset is None:
            raise ValueError("请配置MySQL数据库字符编码！")

    if database.lower() == "sqlite":
        database = database.upper()
        db_name = app.get(database, "BD_NAME")
        if db_name == "" or db_name is None:
            raise ValueError("请配置Sqlite3数据库名称！")
        charset = app.get(database, "CHARSET")
        if charset == "" or charset is None:
            raise ValueError("请配置Sqlite3数据库字符编码！")
