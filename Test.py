#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Author : bajins https://www.bajins.com
# @File : Test.py
# @Version: 1.0.0
# @Time : 5050/9/30 13:00
# @Project: scripts_python
# @Package:
# @Software: PyCharm
# 单元测试框架，主要由四部分组成：测试固件、测试用例、测试套件、测试执行器
import os
import random
import time
import unittest


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):  # 启动执行一次
        print("execute setUpClass".center(50, "="))

    @classmethod
    def tearDownClass(cls):  # 结束执行一次
        print("execute tearDownClass".center(50, "="))

    def setUp(self):  # 每条用例执行前都要执行
        print("execute setUp".center(50, "="))

    def tearDown(self):  # 每条用例执行后都要执行
        print("execute tearDown".center(50, "="))

    def test_one(self):  # 注意所有测试方法都需要以test开头
        print('execute test_one'.center(50, "="))
        self.assertTrue('FOO'.isupper())

    def testReptileUtil(self):
        # download_taobao_chromedriver()
        # download_chromedriver()
        from utils.ReptileUtil import SafeDriver
        safe_driver = SafeDriver("https://www.bajins.com")  # 触发__del__
        # 仅仅从功能上来说，instance 变量与safe_driver变量完全一样
        # 所不同的是，使用with启用上下文管理器以后，在退出缩进的时候会执行__exit__中的内容。
        with SafeDriver("https://www.bajins.com") as instance:  # 触发__exit__
            pass
        with safe_driver.driver as driver:
            pass

    def testSystemUtil(self):
        # print(get_windows_software())
        from utils.SystemUtil import restart_process
        restart_process(os.path.abspath(__file__))

    def testStringUtil(self):
        # print(random.randint(1, 10))
        # print(random.randint(5000, 5017))
        # from utils.StringUtil import is_empty
        # is_empty("")
        from utils import StringUtil
        print(StringUtil.hump_case_underline_lower("oneHTTPRequest12AaureBBBXu"))
        print(StringUtil.underline2hump("hello_word"))
        print(StringUtil.hump2underline("URLCamelCaseHello12Word"))
        json_str = """{"userName":"hi"}"""
        print(StringUtil.json_hump2underline(json_str))

    def testFileUtil(self):
        from utils.FileUtil import count_dir_size
        print(count_dir_size("images"))
        from utils.FileUtil import size_unit_format
        print(size_unit_format(25635891))

    def testMultipartFileUtil(self):
        # t = DownloadWorkerThread(r'http://a3.kuaihou.com/ruanjian/ucdnb.zip', 'd:\\ucdnb.zip', header)
        # t.start()
        url = input(u"The URL Waiting for downloading:")
        filename = input(u"The Filepath to save:")
        from utils.MultipartFileUtil import download
        t = download(url, filename)
        while t.is_alive():
            time.sleep(60)
        print("bye")

    def testDatabaseUtil(self):
        from utils.DatabaseUtil import Sqlite3
        s3 = Sqlite3("test")
        s3.excel_to_db_com(r"./test.xlsx", "test", password="test")


if __name__ == '__main__':
    unittest.main()  # 测试所有
