#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# @Author : Administrator
# @File : DatabaseUtil.py
# @Version: 1.0.0
# @Time : 2019/8/16 13:02
# @Project: scripts_python
# @Package: 
# @Software: PyCharm
import os
import re
import sqlite3

import pandas
import pymysql
import pythoncom

from . import StringUtil


def dict_factory(cursor, row):
    """
    数据查询以字典形式返回
    https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    :param cursor:
    :param row:
    :return:
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def select(connect, sql):
    """
    游标对象执行SQL
    :param sql:
    :param connect:
    :return:
    """
    try:
        connect.row_factory = dict_factory
        # 创建一个游标对象 cursor
        cursor = connect.cursor()
        # 执行SQL
        cursor.execute(sql)
        # 使用 fetchone() 方法获取单条数据.
        # data = cursor.fetchone()
        # 获取所有数据
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(sql)
        raise e
    finally:
        # 关闭游标
        cursor.close()


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
    except sqlite3.OperationalError as e:
        print(sql)
        raise e
    finally:
        # 关闭游标
        cursor.close()


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


def excel_to_db(connect, cursor, excel_name, table_name, sheet_index=0, sheet_start_index=1):
    """
    excel转化为sqlite数据库表
    :param connect: 连接
    :param cursor: 游标
    :param excel_name: 包含excel名的路径
    :param sheet_index: excel中sheet位置
    :param table_name: 数据库表名
    :param sheet_start_index: 数据开始计算的行数，如第0行是表头，第1行及之后是数据
    :return:
    """
    from openpyxl import Workbook, load_workbook

    # 打开excel工作簿
    # 如果是只读的操作，最好加上data_only = True,否则，有些用函数，例如sum计算出来的值就会显示公式而不是内容
    # readonly = True，否则，打开大文件的时候会很慢
    workbook = load_workbook(excel_name, data_only=True, readonly=True)
    # 获取sheets工作表索引
    sheet = workbook.sheets()[sheet_index]
    # sheet_name = workbook.sheet_names()[sheet_index]
    # sheet = workbook.sheet_by_name(sheet_name)

    field_names = sheet.row_values(0)  # 得到表头字段名
    # 通过fieldNames解析出字段名
    names = ""  # 字段名，用于插入数据
    field_types = ""  # 字段名及字段类型，用于创建表
    for index in range(field_names.__len__()):
        # 替换除中文字母数字空格下划线以外的内容
        field_name = re.sub(r"[^\u4E00-\u9FA5A-Za-z\d\s_]", "", field_names[index], 0, re.I)
        # 替换空格为下划线
        field_name = re.sub(r"\s", "_", field_name, 0, re.I)
        field_name = StringUtil.hump2underline(field_name)
        names += f"{field_name},"
        field_types += f"{field_name} TEXT,"
    names = names[:-1]
    field_types = field_types[:-1]
    cursor.execute(
        f'create table if not exists {table_name}(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,{field_types})')
    connect.commit()

    # 读取行
    for row_id in range(sheet_start_index, sheet.nrows):
        # 当前行的所有值
        field_values = sheet.row_values(row_id)
        # 通过fieldValues解析出字段对应的值
        values = ""
        # 读取列 sheet.ncols
        for index in range(field_values.__len__()):
            cell_value = str((field_values[index]))
            if isinstance(field_values[index], float):
                # 读取的excel数据会自动变为浮点型，这里转化为文本
                cell_value = str(int(field_values[index]))
            elif isinstance(cell_value, str):
                # 替换除'"
                cell_value = re.sub(r"'|\"", "", cell_value, 0, re.I)
            values += f"'{cell_value}',"
        # 将fieldValues解析出的值插入数据库
        sql = f'insert into {table_name}({names}) values({values[:-1]})'
        cursor.execute(sql)
        connect.commit()


def excel_to_db_com(connect, cursor, excel_name, table_name, sheet_index=0, sheet_start_index=1, password=None):
    """
    excel转化为sqlite数据库表 https://github.com/mhammond/pywin32
    :param connect: 连接
    :param cursor: 游标
    :param excel_name: 包含excel名的路径
    :param sheet_index: excel中sheet位置
    :param table_name: 数据库表名
    :param sheet_start_index: 数据开始计算的行数，如第0行是表头，第1行及之后是数据
    :param password: 密码
    :return:
    """
    # pip install pywin32
    from win32com.client import Dispatch
    pythoncom.CoInitialize()
    xl_app = Dispatch("Excel.Application")
    xl_app.Visible = False  # True代表Excel在前台打开，False是在后台打开
    xl_app.DisplayAlerts = 0  # 不显示警告信息
    # 打开工作薄，eadOnly为FALSE时，必须输入WriteRedPassword的密码
    workbook = xl_app.Workbooks.Open(excel_name, False, True, None, Password=password)
    # 打开工作表
    sheet = workbook.Worksheets[sheet_index]
    # 获取行数
    rows = sheet.UsedRange.Rows.Count
    # 获取列数
    col = sheet.UsedRange.Columns.Count

    # 通过fieldNames解析出字段名
    names = ""  # 字段名，用于插入数据
    field_types = ""  # 字段名及字段类型，用于创建表
    for index in range(col):
        # 获取每个单元格的值，由于cells的索引是从1开始的，故在原有数据的行数和列数的基础上+1
        field_name = sheet.Cells(index + 1).Value  # 得到表头字段名
        # 替换除中文字母数字空格下划线以外的内容
        field_name = re.sub(r"[^\u4E00-\u9FA5A-Za-z\d\s_]", "", field_name, 0, re.I)
        # 替换空格为下划线
        field_name = re.sub(r"\s", "_", field_name, 0, re.I)
        field_name = StringUtil.hump2underline(field_name)
        names += f"{field_name},"
        field_types += f"{field_name} TEXT,"
    names = names[:-1]
    field_types = field_types[:-1]
    cursor.execute(
        f'create table if not exists {table_name}(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,{field_types})')
    connect.commit()

    # 读取行，不读取第一行
    for row_id in range(sheet_start_index, rows):
        # 通过fieldValues解析出字段对应的值
        values = ""
        # 读取列 sheet.ncols
        for index in range(col):
            # 获取每个单元格的值，由于cells的索引是从1开始的，故在原有数据的行数和列数的基础上+1
            cell_value = sheet.Cells(row_id + 1, index + 1).Value
            if isinstance(cell_value, float):
                # 读取的excel数据会自动变为浮点型，这里转化为文本
                cell_value = str(int(cell_value))
            elif isinstance(cell_value, str):
                # 替换除'"
                cell_value = re.sub(r"'|\"", "", cell_value, 0, re.I)
            values += f"'{cell_value}',"
        # 将fieldValues解析出的值插入数据库
        sql = f'insert into {table_name}({names}) values({values[:-1]})'
        cursor.execute(sql)
        connect.commit()
    # 关闭工作薄
    workbook.Close(SaveChanges=0)
    # 判断当前Excel进程是否还开启着其他的文档，如果没有就结束该进程
    if xl_app.Workbooks.Count <= 1:
        xl_app.Quit()
    del xl_app
    pythoncom.CoUninitialize()


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
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭数据库连接
        self.connect.close()

    def __del__(self):
        self.cursor.close()
        # 关闭数据库连接
        self.connect.close()

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
        execute_commit(self.conn, sql)

    def select(self, sql):
        """
        更新数据
        :param sql:
        :return:
        """
        return select(self.conn, sql)

    def is_table_exist(self, table):
        """
        查询表是否存在
        :param table: 表名
        :return:
        """
        return is_table_exist(self.conn, table)

    def pandas_select(self, sql):
        """
        用pandas库的read_sql获取Mysql数据库数据
        :param sql:
        :return:
        """
        try:
            return pandas.read_sql(sql, self.conn)
        finally:
            # 关闭数据库连接
            self.conn.close()


class Sqlite3:
    def __init__(self, database, charset="UTF-8"):
        """
        初始化Sqlite3配置
        :param database: 数据库
        :param charset: 字符编码，默认UTF-8
        """
        self.db = database
        self.charset = charset
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    # def __enter__(self):
    #     """
    #     https://gist.githubusercontent.com/miku/6522074/raw
    #     获取连接，返回游标
    #     :return:
    #     """
    #     self.conn = sqlite3.connect(self.db)
    #     self.cursor = self.conn.cursor()
    #     return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭数据库连接
        self.conn.close()

    def __del__(self):
        self.cursor.close()
        # 关闭数据库连接
        self.conn.close()

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

    def execute_commit(self, sql):
        """
        插入数据、更新数据、删除数据
        :param sql:
        :return:
        """
        return execute_commit(self.conn, sql)

    def select(self, sql):
        """
        更新数据
        :param sql:
        :return:
        """
        return select(self.conn, sql)

    def is_table_exist(self, table):
        """
        查询表是否存在
        :param table: 表名
        :return:
        """
        return is_table_exist(self.conn, table)

    def excel_to_db(self, excel_name, table_name, sheet_index=0, sheet_start_index=1):
        excel_to_db(self.conn, self.cursor, excel_name, table_name, sheet_index, sheet_start_index)

    def excel_to_db_com(self, excel_name, table_name, sheet_index=0, sheet_start_index=1, password=None):
        excel_to_db_com(self.conn, self.cursor, excel_name, table_name, sheet_index, sheet_start_index, password)
