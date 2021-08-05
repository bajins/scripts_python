#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : https://www.bajins.com
# @Description : https://www.bajins.com/System/%E6%8C%82%E8%BD%BD%E7%BD%91%E7%9B%98.html#rclone
# @File : rclone_expect_config.py
# @Version: 1.1.0
# @Time : 2020/7/26 11:00
# @Project: scripts_python
# @Package:
# @Software: PyCharm

import json
# 如果import urllib，则在使用urllib.request时会报错
import urllib.request
import subprocess
import os
import time
import sys
# 自动执行命令，pip install pexpect
import pexpect
import zipfile
import shutil
import stat

os.chdir('/home')  # 改变当前工作目录，在Jupyter Notebook中使用 %cd /home


def run_cmd(cmd, popen=True, daemon=False, log_path="rclone.log"):
    """
    执行命令并根据参数决定是否在控制台输出执行结果
    :param cmd:  执行的命令
    :param popen:  是否回显，默认显示回显到控制台
    :param daemon:  是否守护进程，默认不启用，当popen=True时才启用
    :param log_path:  日志文件路径，在popen=False时启用
    :return:
    """
    if not popen:  # 执行命令不输出回显并保存执行结果到日志文件（后台运行）
        call = subprocess.call(f'nohup {cmd} >{log_path} &', shell=True)
        if call != 0:
            print(f"执行失败，请查看{log_path}中的日志")
    else:  # 执行shell命令并实时输出回显
        if daemon:
            # 将当前进程fork为一个守护进程
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                sys.exit(0)
        # universal_newlines=True, bufsize=1
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        # 判断子进程是否结束
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:
                print(line.decode("utf8", 'ignore'))


def download_rclone():
    """
    通过GitHub的api下载rclone最新版本
    :return:
    """
    # 判断系统架构位数
    if sys.maxsize > 2 ** 32:
        maxbit = "linux-amd64.zip"
    else:
        maxbit = "linux-386.zip"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    # 请求GitHub api
    req = urllib.request.Request("https://api.github.com/repos/rclone/rclone/releases/latest",
                                 headers={"User-Agent": user_agent}, method='GET')
    res = urllib.request.urlopen(req, timeout=30)
    # 获取到GitHub返回的release详情
    res_json = json.loads(res.read().decode("utf-8"))

    for asset in res_json["assets"]:
        # 如果系统架构在当前name中
        if maxbit in asset["name"]:
            # 获取当前系统架构的下载链接
            download_url = asset["browser_download_url"]
            # rclone压缩包名
            zip_name = asset["name"]
            if os.path.exists(zip_name):
                # 删除同名压缩包
                os.remove(zip_name)
            # 解压后目录名
            dir_name = zip_name.replace(".zip", "")
            if os.path.exists(dir_name):
                # 删除同名目录，防止目录中的文件已被删除
                shutil.rmtree(dir_name)
            # 下载当前系统架构的文件
            # 创建一个opener对象
            opener = urllib.request.build_opener()
            # 向opener传入请求头信息
            opener.addheaders.append(('User-agent', user_agent))
            # 将创建好的opener对象装入request
            urllib.request.install_opener(opener)
            filename, res = urllib.request.urlretrieve(download_url, zip_name)
            # 从urlretrieve调用中清理临时文件
            urllib.request.urlcleanup()
            if not os.path.exists(filename):
                raise Exception("rclone下载失败！")
            if zipfile.is_zipfile(zip_name):
                # 解压
                with zipfile.ZipFile(zip_name, "r") as zip_obj:
                    zip_obj.extractall(path=".")
            # 授权：https://blog.csdn.net/u013632755/article/details/106599210
            # os.chmod(dir_name, stat.S_IRWXO + stat.S_IRWXO + stat.S_IRWXO + stat.S_IRWXO)
            subprocess.run(['chmod', "-R", "777", dir_name], universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=False)
            return dir_name


def auto_rclone_config_start(rclone_dir, storage, drive_name):
    """
    自动配置开始
    :param rclone_dir:  rclone运行目录
    :param storage:
        rclone 15.4之前版本 Microsoft OneDrive:23 , Google Drive:13
        rclone 15.4之后版本 Microsoft OneDrive:26 , Google Drive:15
    :param drive_name:  自定义远程配置名称
    :return:
    """
    child = pexpect.spawn(f'./{rclone_dir}/rclone config', timeout=20)
    # 动态保存每一次expect后的所有内容. before/after都依赖此内容
    # print(child.buffer.decode())
    # print(child.read().decode())
    # 如果返回0说明匹配到了异常
    index = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'New remote'])
    if index == 0:
        pass
    elif index == 1:
        pass
    elif index == 2:
        # n新建远程
        child.sendline('n')

    index = child.expect([pexpect.EOF, 'name'])
    if index == 1:
        child.sendline(drive_name)

    try:
        index = child.expect([pexpect.EOF, 'already exists'])
        if index == 1:
            print(f"{drive_name} 该远程配置已经存在")
            time.sleep(2)
            return None
    except pexpect.TIMEOUT:  # 匹配不上将抛出超时异常
        pass

    index = child.expect([pexpect.EOF, 'Storage'])
    if index == 1:
        child.sendline(storage)

    index = child.expect([pexpect.EOF, 'client_id'])
    if index == 1:
        child.sendline('')

    index = child.expect([pexpect.EOF, 'client_secret'])
    if index == 1:
        child.sendline('')

    return child


def auto_rclone_config_end(child):
    """
    自动配置结束
    :param child: 应用程序子进程
    :return:
    """
    index = child.expect([pexpect.EOF, 'Yes this is OK'])
    if index == 1:
        child.sendline('y')

    index = child.expect([pexpect.EOF, 'Quit config'])
    if index == 1:
        # 输入q，退出配置；n新建；d删除；r重命名；c复制；s设置密码
        child.sendline('q')
    #     print(subprocess.getoutput(f'./{dir_name}/rclone config show'))
    time.sleep(2)


def one_drive(rclone_dir, drive_name, region="1", access_token=None):
    """
    One Drive 配置
    api返回错误信息：https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/concepts/errors
    :param rclone_dir:  rclone运行目录
    :param drive_name:  自定义远程配置名称
    :param region: 1全球（回车默认），2美国，3德国，4中国
    :param access_token:  授权token，为执行 rclone authorize "onedrive" 获取到的token
    :return:
    """
    child = auto_rclone_config_start(rclone_dir, "26", drive_name)
    if child is None:
        return

    index = child.expect([pexpect.EOF, 'region'])
    if index == 1:
        child.sendline(region)
    index = child.expect([pexpect.EOF, 'Edit advanced config'])
    if index == 1:
        # 是否配置高级设置，这里我们直接No，选择n
        child.sendline('n')

    index = child.expect([pexpect.EOF, 'Use auto config'])
    if index == 1:
        # 是否使用自动设置，同样直接NO，选择n
        child.sendline('n')

    index = child.expect([pexpect.EOF, 'config_token'])
    if index == 1:
        # 如果传入的授权为空，就在文件中获取
        if access_token is None:
            # 创建空文件，把授权后的代码保存到此文件中第一行
            # echo 授权代码 >one_drive_access_token.txt
            os.mknod("one_drive_access_token.txt")
            # 等待用户操作时间，秒为单位
            time.sleep(240)
            # 读取文件中第一行内容
            with open("one_drive_access_token.txt", "r") as f:
                access_token = f.readlines()
            if access_token == "":
                raise Exception("读取到授权文件为空，如果操作时间过长，请调整time.sleep")
        # 这里输入在Windows下CMD中获取的access_token
        child.sendline(access_token)

    index = child.expect([pexpect.EOF, 'config_type'])
    if index == 1:
        # 1 onedrive、2 sharepoint、3 url、4 search、5 driveid、6 siteid、7 path
        child.sendline('1')

    try:
        # 授权出现错误
        index = child.expect([pexpect.EOF, 'Failed to query available drives'])
        if index == 1:
            # 动态保存每一次expect后的所有内容. before/after都依赖此内容
            buffer = child.buffer.decode()
            print(buffer)
            if "HTTP error 429 (429 Too Many Requests)" in buffer:
                raise ValueError("429请求太多：请等待一段时间后再次尝试！")
            # 抛出授权出现错误异常
            raise ValueError(f"""{drive_name} 授权出现错误，请重新执行 ./rclone.exe authorize "onedrive" 以获取新的token """)
    except pexpect.TIMEOUT:  # 匹配不上将抛出超时异常
        pass

    index = child.expect([pexpect.EOF, "Drive OK?"])  # Found drive 'root' of type 'business'
    if index == 1:
        # 找到类型为“business”的驱动器 "root"，输入y
        child.sendline('y')

    auto_rclone_config_end(child)


def google_drive(rclone_dir, drive_name):
    """
    Google Drive 远程配置
    api返回错误信息：https://developers.google.com/drive/api/v3/handle-errors
    :param rclone_dir: rclone运行目录
    :param drive_name: 自定义远程配置名称
    :return:
    """
    child = auto_rclone_config_start(rclone_dir, "15", drive_name)
    if child is None:
        return

    index = child.expect([pexpect.EOF, 'scope'])
    if index == 1:
        # 1完全访问所有文件，但“应用程序数据文件夹”除外
        # 2仅只读访问由rclone创建的文件
        # 3在驱动器网站上可见，允许对“应用程序数据”文件夹进行读写访问
        # 4在驱动器网站上不可见，允许对文件元数据进行只读访问
        # 5不允许任何访问来读取或下载文件内容
        child.sendline('1')

    index = child.expect([pexpect.EOF, 'root_folder_id'])
    if index == 1:
        child.sendline('')

    index = child.expect([pexpect.EOF, 'service_account_file'])
    if index == 1:
        child.sendline('')

    index = child.expect([pexpect.EOF, 'Edit advanced config'])
    if index == 1:
        child.sendline('n')

    index = child.expect([pexpect.EOF, 'Use auto config'])
    if index == 1:
        child.sendline('n')

    index = child.expect([pexpect.EOF, 'Enter verification code'])
    print(child.before)
    if index == 1:
        # 创建空文件，把授权后的代码保存到此文件中第一行
        # echo 授权代码 >google_drive_verification_code.txt
        os.mknod("google_drive_verification_code.txt")
        # 等待用户操作时间，秒为单位
        time.sleep(120)
        # 读取文件中第一行内容
        with open("google_drive_verification_code.txt", "r") as f:
            google_drive_verification_code = f.readlines()
        if google_drive_verification_code == "":
            raise Exception("读取到授权文件为空，如果操作时间过长，请调整time.sleep")
        child.sendline(google_drive_verification_code)

    index = child.expect([pexpect.EOF, 'Configure this as a team drive'])
    if index == 1:
        child.sendline('n')

    auto_rclone_config_end(child)


def write_google_drive_config(rclone_dir, name, token=None, drive_type="drive", scope="drive", team_drive=None,
                              root_folder_id=None, shared_with_me=None, service_account_file=None, saf=None):
    """
    此函数是为了方便写入在其他地方已经授权复制过来的Google Drive配置，而不需要重新创建配置
    :param name: 自定义远程配置名称
    :param token: 授权token
    :param drive_type: drive类型，一般默认即可
    :param scope: rclone从驱动器请求访问时应使用的范围，对应--drive-scope参数
    :param team_drive: 团队驱动器的ID，对应--drive-team-drive参数
    :param root_folder_id: 根文件夹的ID，对应--drive-root-folder-id参数
    :param shared_with_me: 只显示与我共享的文件，对应--drive-shared-with-me参数
    :param saf: 服务帐户凭据JSON文件内容，此参数有值且service_account_file为空时默认saf.json
    :param service_account_file: 服务帐户凭据JSON文件路径，对应--drive-service-account-file参数
    :return:
    """
    import configparser
    conf = configparser.ConfigParser()
    # 获取rclone配置文件的路径
    file = subprocess.getoutput(f"./{rclone_dir}/rclone config file")
    file = file.split("\n")
    file = file[len(file) - 1]
    # 读取配置
    conf.read(file, encoding="utf-8")
    # 获取配置中的远程节点
    node_array = conf.sections()
    # 如果远程节点不存在
    if name not in node_array:
        # 添加远程节点
        conf.add_section(name)
        conf.set(name, 'type', drive_type)
        conf.set(name, 'scope', scope)
        if token is not None:
            conf.set(name, 'token', token)
        if team_drive is not None:
            conf.set(name, 'team_drive', team_drive)
        if root_folder_id is not None:
            conf.set(name, 'root_folder_id', root_folder_id)
        if shared_with_me is not None:
            # "true" 或 ”false"
            conf.set(name, 'shared_with_me', shared_with_me)
        if saf is not None:
            if service_account_file is None:
                service_account_file = "saf.json"
            with open(service_account_file, 'w') as f:
                f.write(saf)
        if service_account_file is not None:
            # 服务账户授权json文件路径 https://rclone.org/drive/#service-account-support
            conf.set(name, 'service_account_file ', service_account_file)
        with open(file, 'w') as f:
            conf.write(f)


"""
以下为执行rclone自动配置
"""

rclone_dir = download_rclone()

one_drive_access_token = """授权"""
one_drive(rclone_dir, "onedrive", "1", one_drive_access_token)

google_drive_token = """授权"""
write_google_drive_config(rclone_dir, "gdrive", google_drive_token)
# 团队盘配置
write_google_drive_config(rclone_dir, "gdrive_team", google_drive_token, team_drive="0AFZsAUl3VSwzUk9PVA")
# 分享链接配置
write_google_drive_config(rclone_dir, "gdrive_stared", google_drive_token,
                          root_folder_id="10USshsyfY01grYZzSHMq60lo1H_WVVZH")

# 服务账户授权json示例
service_account_json = r"""
{
  "type": "service_account",
  "project_id": "elated-emitter-287202",
  "private_key_id": "4fcf7adfcfb7ee765170156d5dd9807aa5801e65",
  "private_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
  "client_email": "rclone@elated-emitter-287202.iam.gserviceaccount.com",
  "client_id": "105227418884970409788",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/rclone%40elated-emitter-287202.iam.gserviceaccount.com"
}
"""
write_google_drive_config(rclone_dir, "gservicedrive", saf=service_account_json)

print(subprocess.getoutput(f'./{rclone_dir}/rclone config show'))

"""
以下为执行rclone命令，如果要后台执行（不在控制台中输出执行结果）请在run_cmd函数中设置参数popen=False
文件过滤：
    https://rclone.org/filtering
    https://p3terx.com/archives/rclone-advanced-user-manual-common-command-parameters.html#toc_11
"""

params = " --multi-thread-cutoff 50M --multi-thread-streams 50 --transfers 100 --checkers 100 --buffer-size 50M" \
         " --cache-chunk-size 50M --tpslimit-burst 2 --ignore-errors -P"
# --fast-list 如果可用，请使用递归列表。使用更多的内存，但更少的事务
# --drive-server-side-across-configs 允许Google Drive服务器端操作跨不同的驱动器，不走本地流量
# --drive-V2-download-min-size 指定最小大小文件使用驱动器v2 API下载

# 复制分享的链接文件或目录到团队盘
# run_cmd(f'./{rclone_dir}/rclone copy --drive-server-side-across-configs gdrive_stared: gdrive_team: {params}')
# 我的云盘同步到团队盘
# run_cmd(f'./{rclone_dir}/rclone sync --drive-server-side-across-configs gdrive: gdrive_team: {params}')
# 查看目录大小，可使用--drive-root-folder-id参数指定其他分享链接ID
# run_cmd(f'./{rclone_dir}/rclone size gdrive_stared: ')
# 通过服务账户授权，指定账户查看网盘大小
# run_cmd(f'./{rclone_dir}/rclone -v --drive-impersonate woytu.com@gmail.com size gservicedrive: ')
run_cmd(f'./{rclone_dir}/rclone sync gdrive:/ onedrive:/ {params}')
# 去重
# run_cmd(f'./{rclone_dir}/rclone dedupe --dedupe-mode oldest gdrive:/ {params}')
