#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description:
# @PreInstall:
# @Author : https://www.bajins.com
# @File : system.py
# @Version: 1.0.0
# @Time : 2020/1/11 22:09
# @Project: python_learning
# @Package:
# @Software: PyCharm
import locale
import os
import platform
import sys


if __name__ == '__main__':
    print('system and bit'.center(40, '-'))
    print(platform.architecture(), '\n')

    print('system and deatial'.center(40, '-'))
    print(platform.platform(), '\n')

    print('system'.center(40, '-'))
    print(platform.system(), '\n')

    print('version'.center(40, '-'))
    print(platform.version(), '\n')

    print('系统信息'.center(40, '-'))
    print(platform.uname(), '\n')

    print("python Version".center(40, '-'))
    print(platform.python_version(), '\n')

    # 返回当前系统所使用的默认字符编码
    print(sys.getdefaultencoding)
    # 返回用于转换Unicode文件名至系统文件名所使用的编码
    print(sys.getfilesystemencoding)
    # 获取默认的区域设置并返回元祖(语言, 编码)
    print(locale.getdefaultlocale)
    # 返回用户设定的文本数据编码
    # 文档提到this function only returns a guess
    print(locale.getpreferredencoding)

    # 将当前进程fork为一个守护进程
    pid = os.fork()
    if pid > 0:
        # 父进程退出
        sys.exit(0)
