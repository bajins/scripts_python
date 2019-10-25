#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : SystemUtil.py
# @Version: 1.0.0
# @Time : 2019/8/22 9:18
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm
import sys
from subprocess import call
from pip._internal.utils.misc import get_installed_distributions
import pkg_resources


def check_version():
    """
    判断python版本
    :return:
    """
    v = sys.version_info
    # v.major 大版本号
    # v.minor 小版本号
    if v.major == 3 and v.minor >= 5:
        return
    print('你当前安装的Python是%d.%d.%d，请使用Python3.6及以上版本' % (v.major, v.minor, v.micro))
    exit(1)


def update_lib():
    """
    更新依赖方式一
    :return:
    """
    packages = [dist.project_name for dist in get_installed_distributions()]
    call("pip install --upgrade" + ' '.join(packages), shell=True)


def update_lib_two():
    """
    更新依赖方式二
    :return:
    """
    packages = [dist.project_name for dist in pkg_resources.working_set]
    call("pip install --upgrade" + ' '.join(packages), shell=True)
