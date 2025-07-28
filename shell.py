#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description:
# @PreInstall:
# @Author : https://www.bajins.com
# @File : shell.py
# @Version: 1.0.0
# @Time : 2020/1/11 22:09
# @Project: python_learning
# @Package:
# @Software: PyCharm
import argparse
import os
import subprocess

if __name__ == '__main__':
    # host=input("请输入数据库IP地址：")
    # port=input("请输入数据库端口：")
    # user=input("请输入数据库用户名：")
    # dbPasswd=input("请输入数据库密码：")
    # database=input("请输入数据库名：")
    # charset=input("请输入数据库字符编码：")
    # dbSQL=input("请输入数据库查询SQL：")

    # 设置参数
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--host', '-host', type=str, default='localhost', help='请输入数据库IP地址')
    parser.add_argument('--port', '-port', type=int, default=3306, help='请输入数据库端口')
    parser.add_argument('--user', '-user', type=str, default='root', help='请输入数据库用户名')
    parser.add_argument('--password', '-pwd', type=str, default=None, help='请输入数据库密码')
    parser.add_argument('--database', '-db', type=str, default=None, help='请输入数据库名')
    parser.add_argument('--charset', '-charset', type=str, default='UTF8', help='请输入数据库字符编码')

    # 获取参数值
    args = parser.parse_args()
    host = args.host
    port = args.port
    user = args.user
    password = args.password
    database = args.database
    charset = args.charset

    # 执行shell命令并实时输出回显
    # universal_newlines=True, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    process = subprocess.Popen("echo 111", shell=True, stderr=subprocess.STDOUT)
    # 判断子进程是否结束
    while process.poll() is None:
        if process.stdout is None:
            continue
        line = process.stdout.readline()
        line = line.strip()
        if line:
            print(line.decode("utf8", 'ignore'))

    # 执行命令并得到结果
    print(subprocess.run("echo 22222", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))

    call = subprocess.call(f'echo 333', shell=True)
    if call != 0:
        print(f"执行失败")

    print(os.system("echo"))
