#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# @Author : Administrator
# @File : DatabaseUtil.py
# @Version: 1.0.0
# @Time : 2019/8/16 13:02
# @Project: reptile-python
# @Package: 
# @Software: PyCharm
import os
import sqlite3
import sys

import pandas
import pymysql


def select(connect, sql):
    """
    游标对象执行SQL
    :param sql:
    :param connect:
    :return:
    """
    try:
        # 创建一个游标对象 cursor
        cursor = connect.cursor()
        # 执行SQL
        cursor.execute(sql)
        # 使用 fetchone() 方法获取单条数据.
        # data = cursor.fetchone()
        # 获取所有数据
        return cursor.fetchall()
    finally:
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        connect.close()


def execute_commit(connect, sql):
    """
    游标对象执行SQL并提交事物
    :param connect:
    :param sql:
    :return:
    """
    try:
        # 创建一个游标对象 cursor
        cursor = connect.cursor()
        # 执行SQL
        cursor.execute(sql)
        # 提交事物
        connect.commit()
        # 插入操作后获得自增ID
        # return cursor.lastrowid
        # 操作后获取成功行数
        # return cursor.arraysize
        return cursor.rowcount
    finally:
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        connect.close()


def is_table_exist(connect, table):
    """
    查询表是否存在
    :param connect: 连接
    :param table: 表名
    :return:
    """
    sql = f"select name from sqlite_master where type='table' and name='{table}'"
    res = select(connect, sql)
    if len(res) == 0:
        return False
    return True


class Mysql:
    def __init__(self, host, port, user, password, database, charset="UTF-8"):
        """
        初始化MySQL配置
        :param host: 连接主机地址
        :param port: 端口
        :param user: 用户
        :param password: 密码
        :param database: 数据库
        :param charset: 字符编码，默认UTF-8
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = database
        self.charset = charset

    def connect(self):
        """
        获取链接
        :return:
        """
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset
        )

    def execute_commit(self, sql):
        """
        插入数据、更新数据、删除数据
        :param sql:
        :return:
        """
        execute_commit(self.connect(), sql)

    def select(self, sql):
        """
        更新数据
        :param sql:
        :return:
        """
        return select(self.connect(), sql)

    def is_table_exist(self, table):
        """
        查询表是否存在
        :param table: 表名
        :return:
        """
        return is_table_exist(self.connect(), table)

    def pandas_select(self, sql):
        """
        用pandas库的read_sql获取Mysql数据库数据
        :param sql:
        :return:
        """
        try:
            # 创建连接
            conn = self.connect()
            return pandas.read_sql(sql, conn)
        finally:
            # 关闭数据库连接
            conn.close()


class Sqlite3:
    def __init__(self, database, charset="UTF-8"):
        """
        初始化Sqlite3配置
        :param database: 数据库
        :param charset: 字符编码，默认UTF-8
        """
        self.db = database
        self.charset = charset
        self.get_path()

    def get_path(self):
        if not self.db.endswith('.db'):
            self.db = self.db + '.db'

        # 分割目录与文件
        p, f = os.path.split(self.db)
        # 判断目录是否存在
        if p != "" and not os.path.exists(p):
            # 目录不存在则创建
            os.mkdir(p)

    # def __enter__(self):
    #     """
    #     https://gist.githubusercontent.com/miku/6522074/raw
    #     获取连接，返回游标
    #     :return:
    #     """
    #     self.conn = sqlite3.connect(self.db)
    #     self.cursor = self.conn.cursor()
    #     return self.cursor
    #
    # def __exit__(self, exc_class, exc, traceback):
    #     self.conn.commit()
    #     self.conn.close()

    def connect(self):
        """
        获取连接，如果数据库不存在，那么它就会被创建，最后将返回一个数据库对象。
        :return:
        """
        conn = sqlite3.connect(self.db)
        # 插入中文字符
        # conn.text_factory = str
        return conn

    def execute_commit(self, sql):
        """
        插入数据、更新数据、删除数据
        :param sql:
        :return:
        """
        return execute_commit(self.connect(), sql)

    def select(self, sql):
        """
        更新数据
        :param sql:
        :return:
        """
        return select(self.connect(), sql)

    def is_table_exist(self, table):
        """
        查询表是否存在
        :param table: 表名
        :return:
        """
        return is_table_exist(self.connect(), table)
