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
        data = cursor.fetchall()

        # 执行结果转化为dataframe
        # data = pandas.DataFrame(list(data))

        # 循环所有数据
        # for d in data:
        #     path=str(d[3])
        #     print(path)
        return data
    finally:
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        connect.close()


def args_join(**kwargs):
    """
    参数组合
    :param kwargs:
    :return:
    """
    sql = []
    for k, v in kwargs:
        sql.append(k + "=" + v)
    return " and ".join(sql)


# *args 表示把传进来的位置参数存储在tuple（元组）args里面
# **kwargs 表示把参数作为字典的健-值对存储在dict（字典）args里面
def select_args(connect, table, **kwargs):
    """
    游标对象执行SQL
    :param connect:
    :param table:
    :param kwargs:
    :return:
    """

    sql = "SELECT * FROM " + table
    if len(kwargs) > 0:
        sql = sql + " WHERE " + args_join(kwargs)

    return select(connect, sql)


def select_limit(connect, table, start, end, **kwargs):
    """
    分页查询Mysql数据库数据
    :param connect:
    :param table: 查询的表
    :param start: 分页从第几条开始
    :param end: 分页获取多少条数据
    :return:
    """
    sql = "SELECT * FROM " + table
    if len(kwargs) > 0:
        sql = sql + " WHERE " + args_join(kwargs)
    sql + " order by id limit " + str(start) + "," + str(end)
    return select(connect, sql)


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
        # return cursor.fetchone()
        # return cursor.fetchall()
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


def insert(connect, sql):
    """
    插入数据
    :param connect:
    :param sql:
    :return:
    """
    return execute_commit(connect, sql)


def update(connect, sql):
    """
    更新数据
    :param connect:
    :param sql:
    :return:
    """
    return execute_commit(connect, sql)


def delete(connect, table, **kwargs):
    """
    删除数据
    :param table:
    :param connect:
    :return:
    """
    sql = "DELETE FROM " + table
    if len(kwargs) > 0:
        sql = sql + " WHERE " + args_join(kwargs)

    return execute_commit(connect, sql)


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
        return pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db,
                               charset=self.charset)

    def pandas_select(self, sql):
        """
        用pandas库的read_sql获取Mysql数据库数据
        :param sql:
        :return:
        """
        # detectionModule("pandas")
        try:
            # 创建连接
            conn = self.connect()
            return pandas.read_sql(sql, conn)
        finally:
            # 关闭数据库连接
            conn.close()

    def pandas_select_limit(self, table, start, end):
        """
        用pandas库的read_sql分页查询Mysql数据库数据
        :param table: 查询的表
        :param start: 分页从第几条开始
        :param end: 分页获取多少条数据
        :return:
        """
        sql = "select * from " + table + " order by id limit " + str(start) + "," + str(end)
        return self.pandas_select(sql)


class Sqlite3:
    def __init__(self, database, charset="UTF-8"):
        """
        初始化Sqlite3配置
        :param database: 数据库
        :param charset: 字符编码，默认UTF-8
        """
        self.db = database
        self.charset = charset

    def connect(self):
        """
        获取连接，如果数据库不存在，那么它就会被创建，最后将返回一个数据库对象。
        :return:
        """
        if not self.db.endswith('.db'):
            self.db = self.db + '.db'

        # 分割目录与文件
        p, f = os.path.split(self.db)
        # 判断目录是否存在
        if p != "" and not os.path.exists(p):
            # 目录不存在则创建
            os.mkdir(p)

        conn = sqlite3.connect(self.db)
        # 插入中文字符
        # conn.text_factory = str
        return conn
