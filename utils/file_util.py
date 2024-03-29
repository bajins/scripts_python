#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description:
# @PreInstall: Pillow
# @Author : bajins https://www.bajins.com
# @File : file_util.py
# @Version: 1.0.0
# @Time : 2019/8/21 15:32
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm
import configparser
import os
import stat
import time
import zipfile

from shutil import copy

# pip install Pillow
from PIL import Image

from . import string_util


def path_join(*path):
    """
    路径拼接
    :param path:路径字符串数组
    :return:
    """
    final_path = ""
    for i in range(len(path)):
        p = path[i]
        if string_util.is_empty(p):
            continue
        if string_util.check_startswith(p):
            p = p[1:]
        if string_util.check_endswith(p):
            p = p[:-1]
        if i == 0:
            final_path = p
        else:
            final_path = os.path.join(final_path, p)


def image_to_bmp(image_path):
    """
    转换图片为bmp格式
    :param image_path:
    :return:
    """
    # 分割路径和文件名
    filepath, filename = os.path.split(image_path)
    # 分割文件的名字和后缀
    filename, extension = os.path.splitext(filename)
    # 替换文件后缀组成新的路径
    new_path = image_path.replace(extension, '.bmp')
    # 打开图片
    bmp_image = Image.open(image_path)
    # 保存为bmp
    bmp_image.save(new_path, "BMP")
    return new_path


def replace_file_content(file, old_str, new_str):
    """
    替换文件中的字符串
    :param file:文件名
    :param old_str:旧字符串
    :param new_str:新字符串
    :return:
    """
    file_data = ""
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line
    with open(file, "w", encoding="utf-8") as f:
        f.write(file_data)


def zip_extract(file_path, pwd):
    """
    解压zip文件
    :param file_path: zip文件路径
    :param pwd: 解压目的地目录
    :return:
    """
    zip_file = zipfile.ZipFile(file_path, "r")
    # ZipFile.namelist(): 获取ZIP文档内所有文件的名称列表
    for fileM in zip_file.namelist():
        zip_file.extract(fileM, pwd)
    zip_file.close()


def parent_path(file):
    """
    获取文件的父级目录
    :param file:文件
    :return:
    """
    return os.path.dirname(os.path.dirname(file))


def remove_read_only(filename):
    """
    清除文件的只读标记
        stat.S_IREAD: windows下设为只读
        stat.S_IWRITE: windows下取消只读
        stat.S_IROTH: 其他用户有读权限
        stat.S_IRGRP: 组用户有读权限
        stat.S_IRUSR: 拥有者具有读权限
    :param filename:
    :return:
    """
    os.chmod(filename, stat.S_IWRITE)


def read_file(file_path):
    """
    读取文件内容
    :param file_path: 文件全路径
    :return:
    """
    # 一次性读入txt文件，并把内容放在变量lines中
    with open(file_path) as lines:
        # 返回的是一个列表，该列表每一个元素是txt文件的每一行
        return lines.readlines()


def read_file_remove_line_feed(file_path):
    """
    读取文件内容并删除换行符
    :param file_path: 文件全路径
    :return:
    """
    # 一次性读入txt文件，并把内容放在变量lines中
    with open(file_path) as lines:
        # 返回的是一个列表，该列表每一个元素是txt文件的每一行
        array = lines.readlines()
        # 使用一个新的列表来装去除换行符\n后的数据
        array2 = []
        # 遍历array中的每个元素
        for i in array:
            # 去掉换行符\n
            i = i.strip('\n')
            # 把去掉换行符的数据放入array2中
            array2.append(i)
        return array2


def write_temp(file_path, lines):
    """
    创建临时文件 import tempfile
    :param file_path:文件全路径
    :param lines:内容
    :return:
    """
    with open(file_path, 'wt') as f:
        f.writelines(lines)
    return f.name


def write_lines(file_path, lines):
    """
    覆盖文件内容，在文件中写入多行
    :param file_path: 文件全路径
    :param lines: 写入内容数组
    :return:
    """
    with open(file_path, "w+") as f:
        f.writelines(lines)
        f.close()


def delete_size(min_size):
    """
    删除小于指定值的文件（单位：K）
    :param min_size:
    :return:
    """
    # 列出目录下的文件
    files = os.listdir(os.getcwd())
    for file in files:
        if os.path.getsize(file) < min_size * 1000:
            # 删除文件
            os.remove(file)
            print(file + " deleted")
    return


def delete_null_file():
    """
    删除所有大小为0的文件
    :return:
    """
    files = os.listdir(os.getcwd())
    for file in files:
        # 获取文件大小
        if os.path.getsize(file) == 0:
            os.remove(file)
            print(file + " deleted.")
    return


def create_file(suffix):
    """
    根据本地时间创建指定后缀的新文件，如果已存在则不创建
    :param suffix: 后缀
    :return:
    """
    # 将指定格式的当前时间以字符串输出
    t = time.strftime('%Y-%m-%d', time.localtime())
    new_file = t + suffix
    if not os.path.exists(new_file):
        f = open(new_file, 'w')
        print(new_file)
        f.close()
        print(new_file + " created.")

    else:
        print(new_file + " already existed.")


class Config:
    def __init__(self, filename):
        """
        配置初始化
        :param filename:配置文件全路径
        """
        self.filename = filename

    def read(self):
        """
        获取配置文件
        :return:
        """
        if self.filename == "" or self.filename is None:
            raise ValueError("请输入正确的配置文件名！")
        if not os.path.exists(self.filename):
            raise ValueError("配置文件不存在！")

        config = configparser.ConfigParser()
        config.read(self.filename)
        return config

    def sections(self):
        """
        获取配置组名
        :return:
        """
        return self.read().sections()

    def get(self, section, key=None):
        """
        获取配置值
        :param section: 配置组名称
        :param key: 配置组中的配置名
        :return:
        """
        if section == "" or section is None:
            raise ValueError("配置组名不能为空！")
        if key != "" and key is not None:
            return self.read()[section][key]

        return self.read()[section]


def count_dir_size(dir_path):
    """
    获取目录大小
    :param dir_path: 目录
    :return:
    """
    size = 0
    for root, dirs, files in os.walk(dir_path):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


def size_unit_format(size, is_speed=False, precision=2):
    """
    文件大小自动转换
    byte      ---- (B)
    kilobyte  ---- (KB)
    megabyte  ---- (MB)
    gigabyte  ---- (GB)
    terabyte  ---- (TB)
    petabyte  ---- (PB)
    exabyte   ---- (EB)
    zettabyte ---- (ZB)
    yottabyte ---- (YB)
    :param size: 大小
    :param is_speed: 是否为传输速率计算(bps/bit)
    :param precision: 精确到小数点位数
    :return:
    """
    if not (isinstance(size, float) or isinstance(size, int)):
        raise TypeError('需要浮点数或整数！')
    if size <= 0:
        raise ValueError('数字必须大于零')
    formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    unit = 1000.0 if is_speed else 1024.0
    for i in formats:
        size /= unit
        if size < unit:
            return f'{round(size, precision)}{i}'
    return f'{round(size, precision)}{i}'


def copy_dir(dir, newdir):
    """
    复制目录到指定位置
    import shutil
    shutil.copytree(user_data, mkdtemp, True)
    import distutils.dir_util
    distutils.dir_util.copy_tree(user_data, mkdtemp)
    :param dir: 需拷贝的文件夹
    :param newdir: 是拷贝的地方
    :return:
    """
    for p in os.listdir(dir):
        filepath = os.path.join(newdir, p)
        old_path = os.path.join(dir, p)
        if os.path.isdir(old_path):
            os.mkdir(filepath)
            copy_dir(old_path, filepath)
        if os.path.isfile(old_path):
            copy(old_path, filepath)
