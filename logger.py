#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description:
# @PreInstall:
# @Author : https://www.bajins.com
# @File : logger.py
# @Version: 1.0.0
# @Time : 2020/1/11 22:09
# @Project: python_learning
# @Package:
# @Software: PyCharm
"""
Logger 暴露了应用程序代码能直接使用的接口。
Filter提供了更好的粒度控制，它可以决定输出哪些日志记录。

Handlers 将（记录器产生的）日志记录发送至合适的目的地。
    logging.StreamHandler -> 控制台输出
    logging.FileHandler  -> 文件输出
    logging.handlers.RotatingFileHandler -> 按照大小自动分割日志文件，一旦达到指定的大小重新生成文件
    logging.handlers.TimedRotatingFileHandler  -> 按照时间自动分割日志文件

Formatter 指明了最终输出中日志记录的布局。
    %(name)s Logger的名字
    %(levelno)s 数字形式的日志级别
    %(levelname)s 文本形式的日志级别
    %(pathname)s 调用日志输出函数的模块的完整路径名，可能没有
    %(filename)s 调用日志输出函数的模块的文件名
    %(module)s 调用日志输出函数的模块名
    %(funcName)s 调用日志输出函数的函数名
    %(lineno)d 调用日志输出函数的语句所在的代码行
    %(created)f 当前时间，用UNIX标准的表示时间的浮点数表示
    %(relativeCreated)d 输出日志信息时的，自Logger创建以来的毫秒数
    %(asctime)s 字符串形式的当前时间。默认格式是“2003-07-0816:49:45,896”。逗号后面的是毫秒
    %(thread)d 线程ID。可能没有
    %(threadName)s 线程名。可能没有
    %(process)d 进程ID。可能没有
    %(message)s 用户输出的消息
"""

import logging

# 创建一个logger
logger = logging.getLogger('mylogger')
# Log等级总开关,低于此级别的都不会记录
logger.setLevel(logging.INFO)
# 再创建一个handler,用于输出到控制台
rf_handler = logging.StreamHandler()  # 默认是sys.stderr
rf_handler.setLevel(logging.DEBUG)
# rf_handler = logging.handlers.TimedRotatingFileHandler(
#     'all.log', when='midnight', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0)
# )
# 定义handler的输出格式
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))

# 创建一个handler，用于写入日志文件
f_handler = logging.FileHandler(filename=r'C:\Users\Administrator\Desktop\logs.log', encoding='utf-8')
# 用于写到file的等级开关
f_handler.setLevel(logging.ERROR)
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

# 将logger添加到handler里面
logger.addHandler(rf_handler)
logger.addHandler(f_handler)

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')

#############################################

import traceback

# 打印堆栈信息
traceback.print_stack()

import sys

# 当前输出文件和行号
print("\033[0;31m[%s@%s]\033[0m" % (__file__, sys._getframe().f_lineno), "test")
