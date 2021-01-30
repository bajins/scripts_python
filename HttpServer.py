#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : https://www.bajins.com
# @Description : 来源于see
# https://github.com/freelamb/simple_http_server
# https://github.com/xinghaixu/web_server
# https://github.com/smilejay/python/blob/master/py2016/SimpleHTTPServerWithUpload.py
# https://github.com/Tallguy297/SimpleHTTPServerWithUpload
# https://github.com/rhmoult/SecurityTools/blob/master/Platform_Independent/Python/httpsWithUpload/src/httpsWithUpload.py
# https://github.com/wonjohnchoi/Simple-Python-File-Server-With-Browse-Upload-and-Authentication
# https://github.com/4d4c/http.server_upload
# @see https://gist.github.com/UniIsland/3346170
# @File : HttpServer.py
# @Version: 1.1.0
# @Time : 2021/01/29 11:25:38
# @Project: scripts_python
# @Package:
# @Software: PyCharm


__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]

import os, sys
import os.path, time
import posixpath
import http.server
import socketserver
import urllib.request, urllib.parse, urllib.error
import html
import shutil
import mimetypes
import os
import platform
import posixpath
import re
import argparse
import base64

from pip._vendor import chardet

try:
    import numpy as np
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy ')
    import numpy as np

try:
    import qrcode
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrcode ')
    import qrcode

try:
    import PIL
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pillow ')

try:
    from io import StringIO
except ImportError:
    from io import StringIO


def fbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def modification_date(filename):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filename)))


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        encoding = f.encoding
        if encoding is None:
            encoding = "utf-8"
            # print(chardet.detect(f.read())['encoding'])
        if f:
            for i in f.readlines():
                if isinstance(i, str):
                    self.wfile.write(i.encode(encoding))
                else:
                    self.wfile.write(i)
            # shutil.copyfileobj(f, self.wfile)
            # self.wfile.writelines(f.readlines())
            f.flush()
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        f = StringIO()
        if r:
            stat = "<strong>Success:</strong>"
        else:
            stat = "<strong>Failed:</strong>"
        f.write(f"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
<head>
    <meta name="viewport" content="width=device-width" charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Upload Result Page</title>
    <style type="text/css">
        * {{font-family: Helvetica; font-size: 16px; }}
        a {{ text-decoration: none; }}
    </style>
</head>
<body>
    <h2>Upload Result Page</h2>
    <hr>
    {stat}
    {info}
    <br>
    <br>
    <a href="{self.headers['referer']}"><button>Back</button></a>
    <hr>
    <small>Powered By: bones7456<br>Check new version
    <a href="https://gist.github.com/UniIsland/3346170" target="_blank">here</a>.
    </small>
</body>
</html>""")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(f.tell()))
        f.seek(0)
        self.end_headers()
        if f:
            for i in f.readlines():
                self.wfile.write(i.encode("utf-8"))
            # shutil.copyfileobj(f, self.wfile)
            f.close()

    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return False, "Content-Type header doesn't contain boundary"
        content_type = content_type.split("=")[1]
        remain_bytes = int(self.headers['content-length'])

        content_disposition = self.headers['Content-Disposition']
        if content_disposition:
            content_disposition = content_disposition.encode('utf-8')

        path = str(self.translate_path(self.path)).encode('utf-8')
        fn = None
        out = None

        uploaded_files = []
        line = self.rfile.readline()
        remain_bytes -= len(line)
        while remain_bytes > 0:
            if b"------WebKitFormBoundary" in line:  # 可能有多个文件，按Content-Type分割
                if out:
                    out.flush()
                    out.close()
                fn = None
                out = None
            if b"Content-Disposition" in line and content_disposition != line:
                content_disposition = line  # 获取当前请求在二进制流中的header
                if fn is None and content_disposition:
                    fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"'.encode('utf-8'),
                                    content_disposition)
                if fn is None:
                    return False, "Can't find out file name..."
                else:
                    fn = fn[0]
                if out is None and fn:
                    try:
                        if platform.system() == "Linux":
                            fn = os.path.join(path, fn.decode('gbk').encode('utf-8'))
                        else:
                            fn = os.path.join(path, fn)
                    except Exception as e:
                        return False, f"""文件名请不要用中文，或者使用IE上传中文名的文件。{e}"""
                    while os.path.exists(fn):  # 如果文件已经存在，则重命名
                        r = fn.rfind(b".")
                        if r != -1:
                            fn = fn[:r] + (time.strftime("%Y%m%d%H%M%S", time.localtime())).encode("utf-8") + fn[r:]
                    r = fn.rfind(b"\\")
                    if r == -1:
                        r = 0
                    else:
                        r += 1
                    uploaded_files.append(fn.decode()[r:])
                    try:
                        out = open(fn, 'wb')
                    except IOError:
                        return False, "Can't create file to write, do you have permission to write?"
            if out:
                # 把二进制流写入文件
                out.write(line)
            line = self.rfile.readline()
            remain_bytes -= len(line)
        info_list = ""
        for i in range(len(uploaded_files)):
            info_list += "<br>" + uploaded_files[i]
        return True, f"""<br><br>{info_list}<br>"""

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        content_type = self.guess_type(path)
        try:
            if "text/plain" not in content_type:
                f = open(path, 'rb')
                content_type += f";charset={chardet.detect(f.read())['encoding']}"
            else:
                f = open(path, 'r', encoding="utf-8")
                content_type += f";charset=utf-8"
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", content_type)
        fs = os.fstat(f.fileno())
        fs_len = fs[6]
        if "text/plain" not in content_type:
            self.send_header("Content-Length", str(fs_len))
        else:
            # 如果不指定Content-Range会报错误net::ERR_CONTENT_LENGTH_MISMATCH：
            # 浏览器认为Content-Length只是当前Range的大小，不是整个文件的大小
            self.send_header("Content-Range", f"bytes 0-{str(fs_len)}/{str(fs_len)}")
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        enc = sys.getfilesystemencoding()
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        display_path = html.escape(urllib.parse.unquote(self.path))
        f.write(f"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
<head>
    <meta name="viewport" content="width=device-width" charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0,
     maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Content-Type" content="text/html; charset={enc}">
    <title>Directory listing for {display_path}</title>
    <style type="text/css">
        * {{font-family: Helvetica; font-size: 16px; }}
        a {{ text-decoration: none; }}
        a:link {{ text-decoration: none; font-weight: bold; color: #0000ff; }}
        a:visited {{ text-decoration: none; font-weight: bold; color: #0000ff; }}
        a:active {{ text-decoration: none; font-weight: bold; color: #0000ff; }}
        a:hover {{ text-decoration: none; font-weight: bold; color: #ff0000; }}
        table {{border-collapse: separate;}}
        th, td {{padding:0px 10px;}}
    </style>
</head>
<body>
    <h2><input type="button" value="主目录" onClick="location='/'">Directory listing for {display_path}</h2>
    <hr>
    <form ENCTYPE="multipart/form-data" method="post">
        <input name="file" type="file" multiple/>
        <input type="submit" value="上传"/>
    </form>
    <hr>
    <table>
        <tr>
            <td>
                <img src="data:image/gif;base64,R0lGODlhGAAYAMIAAP///7+/v7u7u1ZWVTc3NwAAAAAAAAAAACH+RFRoaXMgaWNvbiB
                pcyBpbiB0aGUgcHVibGljIGRvbWFpbi4gMTk5NSBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tACH5BAEAAAEALAAAAAAYABg
                AAANKGLrc/jBKNgIhM4rLcaZWd33KJnJkdaKZuXqTugYFeSpFTVpLnj86oM/n+DWGyCAuyUQymlDiMtrsUavP6xCizUB3NCW4Ny6
                bJwkAOw==" alt="[PARENTDIR]" width="24" height="24">
            </td>
            <td>
                <a href="../" >Parent Directory</a>
            </td>
        </tr>""")
        for name in list:
            dir_image = 'data:image/gif;base64,R0lGODlhGAAYAMIAAP///7+/v7u7u1ZWVTc3NwAAAAAAAAAAACH' \
                        '+RFRoaXMgaWNvbiBpcyBpbiB0aGUgcHVibGljIGRvbWFpbi4gMTk5NSBLZXZpbiBIdWdoZXMsIGtldmluaEBla' \
                        'XQuY29tACH5BAEAAAEALAAAAAAYABgAAANdGLrc/jAuQaulQwYBuv9cFnFfSYoPWXoq2qgrALsTYN+4QOg6veFAG2' \
                        'FIdMCCNgvBiAxWlq8mUseUBqGMoxWArW1xXYXWGv59b+WxNH1GV9vsNvd9jsMhxLw+70gAADs= '
            fullname = os.path.join(path, name)
            display_name = link_name = name
            fsize = fbytes(os.path.getsize(fullname))
            created_date = time.ctime(os.path.getctime(fullname))
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                dir_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP' \
                            '+gvaeTAAAFlUlEQVR4nO3dfUxVZRwH8O9z30AmBF6ncUEul8gmV0ylzLes1h' \
                            '+9OedqUVvMps2XBbVsc7U1ajOrlZvTrdocWzS3spVlI2C6stxCVnOo1b3TrhiHlwkIAsIFr' \
                            '/ft6Y9b6BWZ57n3nMMD/D7/MA7nPOe3++P3POd5DpwDEEIIIYQQQgghhBBCCCFEYyzZBgoLC1M4T50TCjGrFgHdjt' \
                            'XKQ4wFLjU3N18z4nxGSygheXnFWcwc3Q6gFMA92oakDgfOg7NDYVtwz0Wfr3ciYtCDcEKcTvcjMOFrALMBwGazwD4' \
                            'rDVarWfPgbiUS4bjc50cgEP5/0wAYK2v9x1NnSAA6E0rIPFfRgyawnwDYVq8owCvb1uC+pXkwmZLu+YRwzuE924W' \
                            'q6kbU1HsAIMI41iqK94ihgehA9SfpcJSkWVMDPnDkbCxbhso3HwdjxibiVg4cPIl3dtUDQC/j1rsV5czARMeUDNX9' \
                            'TJbd/jIDShcvysUne541vCrGc29xDtra+3DOdymNmSKDA/09DRMdUzIsqvdkeBoAtmxaOSYZ53zd+LSqAY2/teBy' \
                            '37AmgTnnZeH4kVcBABWvH8LJU21YvcKF8i1rUOCyx+27eeMqHP7hL0Q5Ww/gA00CmCCqf82dLncPgNlNDTswKytt' \
                            'dHvdUS/e3lmPbZtXYe0TC5E9N0OPONHZPYiaOg+qqhvx4a51ePSh+XE/X1DyHg8EwldaW7xZugRgEPUVAtgBICtz' \
                            'xuiG5gu9qNxZjwNVZVhYlK11bHGy52Zg66aVWLnchY1bv8B3X76EvHnXP/s7MmawQGAoU9cgDGAS2JcBiBvI91ef' \
                            'wKYNy3VPxo2Ki7Lx4gvLsP+zRsPOaSSRhPCbNzQ0XsC6JxdqGI46654qxvFfz8dtS02JFbvDUZJ2q2MmC5Eui+Om' \
                            'Maen148ch/G9RK4jE6mp8aEvKs5Ba3s/rCmBj3ILFuwzhS0RI2Ixm/lwS4unW6v2RBIyRiTCYTYbf/lrNjMcq62I' \
                            '27a94mEc++VvPnI1VG7mpnKYo4bEEgXgdLk7GEelong/T7a9pBIiE5fTjtpvt7K9Hx+H52wnwmFjEhIKRdDZNZjL' \
                            'Garz890BRfF+lUx7ol2W1FxOO/btfsbw854604HSDdU8Eom+ASCphIgM6mQcSxfnovCu2QCQ9BVOUglx5dtvv9M0' \
                            'YbOYGTQYAoQvezm/3nP9XFcx7s4kMdRlSSaBCtEpEgKAKkQ6wpe9Uc5h+m/Cvv65KvzhuahHXJOW0+W+uQ/5vbXF' \
                            'u1zt8cIVwm5YPaFkqPKAyM7Cl2l87JIWfCeWiDYzLcxfdVr4mKRWe4n2xAd1SouukpoYEu0Zstpb8pgHQ/6Qbu2n' \
                            'z7Si6ajxN8r0IHzZm0iFDPlDeK1yt/Bxau19d4dubRuNJoaSoaUTyVCFSIYqRDJUIZKheYhkqEIkQ2OIZAyZqafP' \
                            'tOo6ectIN+T/TQ0hPlNPYHVxqixrGCGB1V7qs/RE90MkI1whVCD6ogqRjHiF6BEFGUUTQ8nQ0olkqEIkQ0snkqEK' \
                            'kQyNIZKhCpEMVYhkaGIoGVo6kQz9sbVkqEIkk8DyO+VFT1QhkqEbVJKhCpEMjSGSSXimHo3Gvsry/N6pIuG1rGA' \
                            'w9gQ9ywQ8UW4qE0lIEMDoQ/BD4VhCrFPmmXRyEEnICAAM+QMAgGAwlhiLhSpESwIJYVcAoH/gKgDAPxwEAKSnG/' \
                            'OaiulCdUIYuA8Amk63AwBalNg7VBx32vSIa9JTOkZfANQncpzqhETBfgSAbw6fQWfXIGqPeAEAS9wzRc43LSgd1/' \
                            'DW+22xbziOihyregBwu902/wj+xAS94mhSYryXRaP3K8o5Re0hqgeAnp6eiH3WnBrOkA8gDwD1VePrB8f3jEefF' \
                            '0kGIYQQQgghhBBCCCGEEEJ08S96MLERXBz0BQAAAABJRU5ErkJggg== '
                display_name = name + "/"
                link_name = name + "/"
                fsize = ''
                created_date = ''
            if os.path.islink(fullname):
                dir_image = 'data:image/gif;base64,R0lGODlhGAAYAPf/AJaWlpqampubm5ycnJ2dnZ6enp+fn6CgoKGhoaKioqOjo6SkpKW' \
                            'lpaampqioqKmpqaqqqqurq6ysrK2tra6urq+vr7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y' \
                            '8vL29vb6+vr+/v8LCwsPDw8bGxtDQ0NTU1NXV1dbW1tfX19jY2Nra2tzc3N3d3eDg4OHh4eLi4uPj4+Tk5OXl5e' \
                            'fn5+np6erq6uvr6+zs7O7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf39/j4+Pr6+vv7+/39/f7+/v///' \
                            'wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                            'AAAAAAAAAAAAAAAAAAAAAAACwAAAAAGAAYAAAI/wCZCBxIsKDBgwgLrsigwUXChEVGYNBwIYKIJA8LFunwocKGDA' \
                            '8ieMg4kAiHDxRmCGyhIAEKkhtR2iCYYYEAkiNQ3ijYIQGAjDkuVFBJsIcBAhcyttCgoSCQBQcUFMn44gIFEiwE/' \
                            'oAqIAfJIREeQLDAZIeCAwO8IuQRowYSIxQgBFhAoQBatQaFiLCQoQIFCxEMREUwoAEPhEA0dMQwQSwCIEFYpKCR8' \
                            'IfiCjWYgJCr4AhJyx13CFRhQYECGBmRcKwgmmAEBCsyltBQQUfBGwUG4MjoYMOIgjsSIJBAskGGEAR3IEhw4AdJEx' \
                            'IeyBCIY/kBHySZLNEwgcGGDQYQNBbPLpAIBgULEhB4AIQ8wRMFBIhQ4j4gADs='
                display_name = name + "@"
            if name.endswith(('.bmp', '.gif', '.jpg', '.png')):
                dir_image = name
            if name.endswith(('.avi', '.mpg')):
                dir_image = 'data:image/gif;base64,R0lGODlhGAAYAMIAAP///7+/v7u7u1ZWVTc3NwAAAAAAAAAAACH' \
                            '+RFRoaXMgaWNvbiBpcyBpbiB0aGUgcHVibGljIGRvbWFpbi4gMTk5NSBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQu' \
                            'Y29tACH5BAEAAAEALAAAAAAYABgAAANvGLrc/jAuQqu99BEh8OXE4GzdYJ4mQIZjNXAwp7oj+MbyKjY6ntstyg03' \
                            'E9ZKPoEKyLMll6UgAUCtVi07xspTYWptqBOUxXM9scfQ2Ttx+sbZifmNbiLpbEUPHy1TrIB1Xx1cFHkBW4VOD' \
                            'mGNjQ4JADs= '
            if name.endswith(('.idx', '.srt', '.sub')):
                dir_image = 'data:image/gif;base64,' \
                            'R0lGODlhGAAYAPf/AAAbDiAfDSoqHjQlADs+J3sxJ0BALERHMk5LN1pSPUZHRk9NQU1OR05ZUFBRRFVXTVdYTVtVQF' \
                            'lVRFtbSF5bTVZWUltbUFlZVFtcVlxdWl5eWl1gWmBiV2FiXWNhXGRjXWlpYmtqZ2xtZmxsaG5ubHJva3Jzb3J0bH' \
                            'N0b3Z5dHd8eXh4dX18dXx/dnt8e31+eahMP4JdWIdnZox4cpVoYKJkXrxqablwcNA6Otg7O/8AAPwHB/0GBvgODv' \
                            'sMDPMbG/ceHvkSEuYqKvYqKvU2NvM6OvQ6OsFQUNVbW8N4eNd0duNeXu9aWvFUVOVqau1jY+1mZu5mZuh5eYSFgI' \
                            'WGgYaFgIiGgYqKiY6LioyMiY2NiYyMio2OiI6OjZCSjZSQi5OSkJGUkpSVk5WVlJWVlZiZlpiZmJ6emp2dnZSko6' \
                            'GhnKGhoKOjoaKnoqSkpKSmpKWmpaampqqrqKurqKqrqq2sqq6urrSyrrCwsLa3tb63tbi4t7q6ur+/vsCbm96Li9' \
                            'iUlMqursmwr9KwsN69veSCguiMjOiOjuaQkOWVleaXmOGfn+aYmOaamuebm+adneecnOeenuiQkOWgoOWsrOasr' \
                            'OWxseW2tue3t+e8vOi+vsHBwcfHx8jIxs7Mx8nJyMvLy8zMy83NzM7Pzs/Pz9PR0dTU1NXV1dXW1tbW1tfX19bb2' \
                            '9jY2NnZ2djb29ra2tvb2tvb29za2tzc3N3d3d7e3t/f3+bCwufDw+fGxuTJyejCwujHx+nHx+vPz+rT0+rU1OrX1' \
                            '+vX1+rY2Ojf3+Hh4eLi4uPj4+Hn5+Tk5OXl5ebm5ufn5+nn5+jo6Onp6erp6evr6+zs7PDn5/Dq6vDt7fHv7/Lu' \
                            '7vPu7vPv7/Dw8PHx8fLy8vPz8/Tx8fbz8/T09PX19fX39/b29vj39/j4+Pn4+Pn5+fr5+fr6+vv7+/z7+/z8/P3' \
                            '9/f7+/v/+/v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAAGAAYAAAI' \
                            '/wDhCRxIsKDBgwgTZis00F27hAbRNSpSaSC7ZM6ePQsXjdmzZekKUpOio0lBVShjJXvYjp07gsEm/dLhqKC2aNG2' \
                            'LesES13BXJTg4dLBi2C7kPDSyQFTRY26c8akZbolkJGOaQTZFTO2LA8KCCA+zDFTp4aggVCCmCtYrJUxNiI4nAjh' \
                            '4o2HGW1CrhvCxGC5cOVqvcCgQQUWGRtanOkG75qOQwXbhWvZ7lOZMIGSsJjihY5AYTowFWRnipUtT6BGWIARY8IX' \
                            'Pc1eXtIxrKC7cqJCjdJCIcIBAwRoaLqU6IkRHthGnwPzoEGKDBISMHDAZWAvHUTWjaa1J42NAgAELMBAMGCNwHbWe' \
                            'kQxqA4VMkBKSokZE8AKtHLpjuHxo0OSQXfuLKJIOHdc0IECFaxgQivpxHGDDpYc9McS5oBTAhxUbNHFFX2I4Q4fR' \
                            '+iwi0GPCCGLK6rYgQYJWZDhBil7cMMJDjpAAg85L8ETCRDVqAONMuGMA0446rDjEzzi5KDDD4j48g48huxAyCqtO' \
                            'DNZOeWcM85DAxEDzDcE+YDEK5u0EostbZ2SyizsQASPE4PAo4466TxVZzptuqmLN266GRAAOw== '
            if name.endswith('.iso'):
                dir_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP' \
                            '+gvaeTAAANQUlEQVRoge2ZW4ykR3XHf6eqvkt3z2VnvevFu8viGG' \
                            '+IbO86IVFi5QGIEFYMtsRLXkiIDBaKFRyIoigoIkFLFMNDFCFbYIhsQxQlQYmyWNgh' \
                            '+MEoUpBtxXkADDZmbWMb33b2Ppfu71ZVJw/V0zOzMzuzdnB44Uit7v6+qv7O//zPOfWvavi5/WxNfho/Mv/Q7XsWG' \
                            '/0swo0x+n70ZF7bvAsBHzt89IAgKM5azSV7aW6mf92B64+88n999usGoHrEPPPN7N' \
                            '+Lnb3fRqN0TUOoK9phS6g9dVfThobaN7Sxm8yzYumXA6YHcxQu74wr7nrbjeFPRI7E/zcAzz50' \
                            '+7FsujxoMsAoGiPdqMUPW/wovWrfUIeGuqvoop/MzU1G7nIKm1O4giwryPuDF401/3Dle//yL95QAM8+ePv7VPR' \
                            '+m4sxfYstXLqhSqg87bDBj2q65ZYmtNRdReXrCQABcltQuiKBMDkiyQXjHFl' \
                            '/8JTD3fbWmz75rYv1yVzswGP3HznaVKMH2mrZdF1L7AIaNd0UAScYazBiERFEFBB0TYxEBGtMesdMnAeI3tMsLvxS' \
                            '21UPHPuPv/6bi/VrWwZUj5hjR/3pbnm4I1owuSPrF9hBRjYosbkFAQ2RdqmhGzZ0yzVN01J1Q6pQ04XEgDWW0paU' \
                            'WUHPFIjZPH7GZWT96W/+4o3+xu1qY0sGVI+YH/1T07UvntkRl2toAtF7QtcR24hvPKqJBTEG4wxiBMFgJMVnLQP' \
                            'GCM4YnLgLOg8QfUe7vHDDM9+Q/1Q9sqWPW9586svDrn1+3sRhjVYBWg9tJLSe0LTEriO2AVK2IM5grCBW0jUDrAA' \
                            'EnDiscVjZvvQ0Bpql5Xc8/XW+97oA/PDv//QFf/ys0aqDxkPj0aqD2qNNINQerbv0Pq4FcTa9LGCEVAYrAAwGgzU' \
                            'WI25bAIhgcgfOXnPsgU8/9JoAHDv6qffFs/WBOGrShagJRBXQ2kPliV2gqzyh7Yhth6pijIxZsAjjAhvX+Ur6WC' \
                            'zbESBGcL0+Wb+PK3tkUzPvfvrrf/XhzcZuGoowbB7wy0OwBkJcD8JI8swoasA3FptZTJHy2lmDN4IRAxh07KwVh' \
                            'xGHtVs3PmMttuzhyh6uLHF5iSkKXJbfA3x5w/jzL/zo6Kfu9KORSC+HXgaFWe1VUaHu0FEHdSDWgTD0+LojVD6l' \
                            'e5YhzjKZFJOIcMbgTIbZouxMluEGU+SDKbL+gKw/RTbok/f79HZfKj/59p1ntwSgesSE6G9RKzDlkIGFXg5lBm7' \
                            'sUNBUB6MOhi2x6fDDjlC3aIwYB2LHPV4EFUUQrGRk9kK5L9iiIO9PkQ+myfvTFNPT5FMDssEMWX+aYmYHvZ17dp' \
                            'zfldb94tNH45+Hru3TdxAsZIJkEXKLNgbqAF1IIEYdSuo4wRm6ymCKDAmCLrTkneESZtiZT+M1EEUxatFxUa/xH' \
                            'dcrycsp3KCPK/tkZQ9blNiywOYlLs8Q6+jt2sWJx69cBvqbAgiE96uOc94K2ByyCFlAMkEzA7VJteAjDNuU41YI' \
                            'ojSnW7QJG+LrVjztImqFkIMaQAxFf4CbniLvDbDjwrV5iSsLXF4i1k5+xxYFNst65+FP9uTR2y+jW3zBhy7blOU' \
                            'QofNQR7Tyk9aKgMyUuH4JCq43zdyhdzD1lqvJZ3cD0C6cYPmFJzj7/W/jqyUQIU5lZDtmyKdmUqr0B7hyQFb2EpPO' \
                            'IZsIhfrECU6cevo33vabn3hsHQM2jD7SxrC585A6ks0hVyQ3aG1g5JC2w1qLtp6Zg29n77t/F5OX66aWu/ZT7trP' \
                            'zkPv5JWH/pHFZ76DORfI9+6ld8lOXG9A1hvgyjKtIxdQOApks7NMnZn7FjANa4o4qv76JH22MiPQz5HZHjJXIFM' \
                            'ZMQSmr7iW/Td8eIPz66bmJfvfewtTVxwmtC3ti8fpz+2iv2Mn+WCAOT/qqmiISb40Lb6uiF2HhjhYGeJWx8a92' \
                            '3u/xqyAFbQNuP40e9/zwbFqUEIInDt3jrquASjLktnZWZxLj9v3ng8yfP4pmvnTdAtDsumZVYejojGgPhCjJ8a' \
                            'IhoDGiGqEGCGu1tkqgBgve00AAKoOVJn7ld9CbUYIgRACp0+dgqX5k7p4/OMA7cyb7jjZ7Nl9ya5dWGvB5sz98' \
                            'rs4+fD9LD3zLMWllxC8B+8JwUMMxKgQxgA0JrkSI6qKb9sJTRMAglwqxkyiuBKRLa1OW8XB5dcQY0q/hYUFWJw/' \
                            'ue+qX710zcivvvSDx4aLed6fnZ0FoH/5NfDw/YxefoXR6XnUKzH6iZOqAQ2afFGFqCgJRGibjQwY54zk+QqYiUx' \
                            'OF8abkxVlqYoq+LiQvg/m8D5p/qZp4OQrf3Q+1vbsqzfr7GX/ujLOTu8EIIxGjOZPgOhYFEY0jp8hmtYa1bEsV1' \
                            'AIbbsJgDzHDvrjxppOEFTSu6ikzwYgaX5UWPrxPIrifYfI6gLZ2bDavFfMxwKg6xJrOnZCFarTJ9KmSMYlLGNnk' \
                            'UkyrF4DaVebzWobzXKyQQ8wGEkiTCTpICMGHcsDEYOxDrGGUa+HXx5SnzmO25l6gLUWnd5zN/DPa/23u/Z9zhgzA' \
                            'dCdmR/fgK6uNuBdZxP5KoiAiTKp4lUGspysPzPRMMYIGIOITdrGGLAOay3GWEzm6O/fy+JTTzN6/kn6MynljTGYnf' \
                            'v6z33v0RNx8eTHAczM7jvM7Jt2GWMmqVY9/4P04OLCS8/EJumcUpdo5jcAcJnTrD8QMYIYCzYxIcZijEkro02fVyIy' \
                            '/dYrEoAnH8Fd+Wvg8tWIz+3bbef2TViIqrQradM1VD98NN3oXcTmZgOgeHwDAMWQ9wdjx1eiblO+n78DUUVDIJubId' \
                            '+1k/bUGZYfuY/8uvez/TmB0jz6NWIzAmch21gu2wPgpQ0AxJiRWDuwvd4FXVAU9YFQN7T1Mn40pPiFvXRnFwgvP0' \
                            'X9yNcw114PWbH5/K4hfvdBOP5MaihekXNNYqFIrF+E82jkkQ0A8l59fXPy9MODA/s3mwM+4NuGUFW0zZAwHNEMh7' \
                            'SjZdg9BScW0VePEU6/SDxwGN19OdrbkYJTnUNOPIf5yePQpdVZQ0z77C4irU97jtJBbrYEYrw2dTu8d+X7umDP/' \
                            '89XdObgwfXOh4Bva3zdENqabjQiVCPaaohfWqYZDUEj+ABnqqRQtzAZ5Ggvh6UaXWyhDcnhMkN6Fi0ckhvIXZI' \
                            'r5wOow39fc8sd121gACD4rvLDUc8N+mjw+LYjtg2+bfB1ja9H+FFFVw/phiNCPVrtEM7CpVPQePxyAmJjipHJH' \
                            'dklA/K9s0RraU4vEaJCFFiqoYswalBvEyulQ3KFXNYDiQoh3rcuIOuirZj5x74SBm95M6FtCW1DaCtCMz7zbCp8M' \
                            '6IbDolNw2ZCI2hg2I1YbpZRhB3FDDtmZyl2zZBN52gbqM6M6BZGxHMVutTBcpsYhMRGbmCFicKBS4yYNpy6+pY794' \
                            'gwWcnWMSBCfO4bJ87aqXIOawltTaxruqbB1xVdXeGrEbHr2NQUutjhQ0dUZeXwLQRFg4eYYzKL62fEriD6gESShBh' \
                            'p2uWFCI1C0MRIBxQGCQpi71vr/AYGVuzH9382lvv2SGiacf7X+KYiVDUxXDjHo0YqP2LYVjShxRrLTD7FdG+acuc' \
                            '0+VyJzRyhDbQLFe1STVio0eUWhi2MutVjnBU2MguFRcosHv7YXRt67qarSH3mxEdi9PfYqR5dW+ObhlCPVk+jL2A' \
                            'hBHyIhLjqhIqgIWn82EZsBsZZbGnJ2ozYj6ARJY6FkV8FEdI1sSB59oHNnrlpv7rq5s/d25w99WBz7hzdaEioqm2' \
                            'dV4WOQNBAGLNskLToEVG/xiEDtsiQ0pH1HFJkSGGRXpZyfk0bFRHMVP7ioVvv+peLBgBw9YfuuKE9dfaJOKq5m' \
                            'K1mJBCiJ0SfdDukIxRJ+kU1EEMkjqNrnMUVDlM4TOmQMk+LWc+tgjCCDLJ4zce+dOBCz91y6Tv0B184rEvVfx' \
                            'G22dig+BCIGggaV0+k1YAKSlq4NCStD+n80+TpWNKWGVJm0M+QnksLWmFhOtNDn7hnS62xJQAR4qE//NK7WGz+' \
                            'DX9hFoJGfAyEGIlrm4SM5UdceUXUh8nSYTKb9iG5xfYMUtjUPjMDg8xf+2f3bqstth0ggh6+7a7fkaXmM9TdcLMx' \
                            'PgYinqBx3U5OWDlij2mPq5pSaIUhEWyRpLnNHDbPEKKS2+9c+8d/dxE6+zX8R3boti9+0vhwE4vVk2tbXdRIjKn' \
                            'zRA2r204Y7+pSDUiMxKDgFV3DptgEgghxsVIX9fcO3/r5t1+sX6/rb9bHP//RT+P4EP38zZ14Wt9QxY7O1/hxCx' \
                            'UgdwWFK+nZgiLPyaYK3KDA9XJsmc6AYt1Rv7qIr9qXr/rA325Ukm8EAEiy4/t3f/TuEPX3W21dZTuq2BDXMJD+D' \
                            'y7ouZLCjQH0C4y1aNVCUILG5YM3fWb2/BX2DQew1r77xVv3dcSH21gf8CFODtecOJx15JJhrYs2tyLWqsnsWVsN' \
                            '33nw5i888dN4/s/tZ2n/C+cR4IqwA3arAAAAAElFTkSuQmCC '
            f.write(f"""<tr>
                            <td>
                                <img src="{dir_image}" width="24" height="24">
                            </td>
                            <td>
                                <a href="{urllib.parse.quote(link_name)}">{html.escape(display_name)}</a>
                            </td>
                            <td style="text-align:right; font-weight: bold; color:#FF0000">{fsize}</td>
                            <td style="text-align:right; font-weight: bold;">{created_date}</td>
                        </tr>""")
        f.write("</table></body></html>")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        # self.send_header("Content-Length", str(f.tell() + 6))

        # 如果不指定Content-Range会报错误net::ERR_CONTENT_LENGTH_MISMATCH：
        # 浏览器认为Content-Length只是当前Range的大小，不是整个文件的大小
        self.send_header("Content-Range", f"bytes 0-{str(f.tell() + 6)}/{str(f.tell() + 6)}")
        self.end_headers()
        f.seek(0)
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


def getip():
    match_ip_dict = {}
    ipconfig_result_list = os.popen('ipconfig').readlines()
    for i in range(0, len(ipconfig_result_list)):
        if re.search(r'IPv4 地址', ipconfig_result_list[i]) is not None:
            match_ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ipconfig_result_list[i]).group(0)
            for j in range(3, 7):
                if re.search(r"无线局域网适配器", ipconfig_result_list[i - j]) is not None:
                    match_ip_dict[ipconfig_result_list[i - j]] = match_ip
    ip_dict = match_ip_dict
    for i in ip_dict:
        return ip_dict[i]


def showTips(bind, port):
    return port


if __name__ == '__main__':
    # http.server.test(SimpleHTTPRequestHandler, http.server.HTTPServer)
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    print('----------------------------------------------------------------------->> ')
    port = args.port
    if not 1024 < port < 65535:
        port = 8080
    print('-------->> 现在，在监听 ' + str(port) + ' 端口 ...')
    with socketserver.TCPServer((args.bind, port), SimpleHTTPRequestHandler) as httpd:
        data = 'http://127.0.0.1:' + str(port)
        if platform.system() == "Windows":
            data = 'http://' + getip() + ':' + str(port)
        print(f'-------->> 您可以访问地址URL:{data}')
        print('-------->> 或扫描此二维码: ')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1
        )
        # from MyQR import myqr
        # myqr.run(
        #     # 在命令后输入链接或者句子作为参数,然后在程序的当前目录中产生相应的二维码图片文件,默认命名为“qrcode.png”
        #     words='helloworld',
        #     version=1,  # 设置容错率为最高默认边长是取决于你输入的信息的长度和使用的纠错等级；而默认纠错等级是最高级的H
        #     level='H',  # 控制纠错水平，范围是L、M、Q、H，从左到右依次升高
        #     picture='test.gif',  # 用来将QR码图像与一张同目录下的图片相结合,产生一张黑白图片,格式可以是.jpg, .png, .bmp, .gif
        #     colorized=True,  # 可以使产生的图片由黑白(False)变为彩色(True)的
        #     contrast=1.0,  # 用以调节图片的对比度，1.0 表示原始图片，更小的值表示更低对比度，更大反之。默认为1.0。
        #     brightness=1.0,  # 用来调节图片的亮度
        # )
        qr.add_data(data)
        qr.make(fit=True)
        qr.print_ascii(out=None, tty=False, invert=False)
        print('----------------------------------------------------------------------->> ')
        httpd.serve_forever()  # 开始监听
