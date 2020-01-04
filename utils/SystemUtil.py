#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins www.bajins.com
# @File : SystemUtil.py
# @Version: 1.0.0
# @Time : 2019/8/22 9:18
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm
import ctypes
import gc
import os
import platform
import sys
from subprocess import call

import psutil


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
    from pip._internal.utils.misc import get_installed_distributions

    packages = [dist.project_name for dist in get_installed_distributions()]
    call("pip install --upgrade" + ' '.join(packages), shell=True)


def update_lib_two():
    """
    更新依赖方式二
    :return:
    """
    import pkg_resources

    packages = [dist.project_name for dist in pkg_resources.working_set]
    call("pip install --upgrade" + ' '.join(packages), shell=True)


def get_windows_software():
    """
    从注册表获取Windows系统安装的软件列表
    :return:
    """
    import winreg

    # 需要遍历的两个注册表
    sub_keys = [
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
    ]

    software_list = {}

    # 连接注册表根键
    regRoot = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    for sub_key in sub_keys:
        keyHandle = winreg.OpenKey(regRoot, sub_key, 0, winreg.KEY_ALL_ACCESS)
        # 获取该目录下所有键的个数(0-下属键个数;1-当前键值个数)
        for i in range(winreg.QueryInfoKey(keyHandle)[0]):
            try:
                # 穷举每个键，获取键名
                key_name = winreg.EnumKey(keyHandle, i)
                key_path = f"{sub_key}\\{key_name}"
                # 根据获取的键名拼接之前的路径作为参数，获取当前键下所属键的控制
                each_key = winreg.OpenKey(regRoot, key_path, 0, winreg.KEY_ALL_ACCESS)
                if winreg.QueryInfoKey(each_key)[1] > 1:
                    # 穷举每个键，获取键名、键值以及数据类型
                    # name, value, type = winreg.EnumValue(each_key, j)
                    # print(name,value,type)
                    DisplayName, REG_SZ = winreg.QueryValueEx(each_key, 'DisplayName')
                    DisplayVersion, REG_SZ = winreg.QueryValueEx(each_key, 'DisplayVersion')
                    software_list[DisplayName] = DisplayVersion
            except WindowsError as e:
                pass
            finally:
                winreg.CloseKey(each_key)

    winreg.CloseKey(keyHandle)
    winreg.CloseKey(regRoot)

    return software_list


def is_admin():
    """
    判断是否为管理员权限
    :return:
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        return False


def update_fire_wall(key_name='PublicProfile'):
    """
    修改注册表中防火墙的公网和家用网络的开启和关闭
    :param key_name: PublicProfile StandardProfile
    :return:
    """
    import winreg

    sub_dir = r'SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy'
    # 连接注册表根键
    regRoot = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    # 获取指定目录下键的控制
    keyHandel = winreg.OpenKey(regRoot, f"{sub_dir}\\{key_name}")
    if is_admin():
        # 设置该键的指定键值enableKey为value
        winreg.SetValueEx(keyHandel, 'EnableFirewall', 1, winreg.REG_DWORD, 1)
    else:
        if sys.version_info[0] == 3:
            # 获取管理员权限
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    # 关闭键的控制
    winreg.CloseKey(keyHandel)
    winreg.CloseKey(regRoot)


def restart_process(path):
    """
    当内存占用达到一定比例进程重启
    :param path: 执行脚本的全路径
    :return:
    """
    if psutil.virtual_memory().percent >= 80:
        print('内存使用：', psutil.Process(os.getpid()).memory_info().rss)
        print("当前内存占用率：", psutil.virtual_memory().percent)
        # if gc.isenabled():
        #     # 释放内存
        #     gc.collect()
        print("前进程id：", os.getpid(), "父进程id：", os.getppid())

        py = "python3" if (os.system("python3 -V") == 0) else "python"
        sysstr = platform.system()
        if sysstr == "Windows":
            os.system(f"taskkill /pid {os.getpgid()} /f && {py} {path}")
        elif sysstr == "Linux":
            os.system(f"kill -9 {os.getpgid()} && {py} {path}")


if __name__ == '__main__':
    # print(get_windows_software())
    restart_process(os.path.abspath(__file__))
