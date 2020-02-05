#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description: 清华大学免费开放“文泉学堂”
# @PreInstall: pip install httpx loguru PyJWT
# @Author : https://www.bajins.com
# @File : wqxuetang.py
# @Version: 1.0.0
# @Time : 2020/2/5 15:01
# @Project: reptile-python
# @Package: 
# @Software: PyCharm

# from typing import Union, Tuple
import os
import sys
from pathlib import Path
from time import time
import json
import httpx
import jwt
from loguru import logger

JWT_SECRET = 'g0NnWdSE8qEjdMD8a1aq12qEYphwErKctvfd3IktWHWiOBpVsgkecur38aBRPn2w'
SESS = httpx.Client()
URL = 'https://lib-nuanxin.wqxuetang.com'
SESS.get(URL)


def gen_jwt_key(book_id):
    # url = "https://lib-nuanxin.wqxuetang.com/v1/read/k?bid=%s" % bookid
    url = f'{URL}/v1/read/k?bid={book_id}'

    # r = SESS.get(url, timeout=5)
    # j = json.loads(r.text)

    resp = SESS.get(url)
    resp.raise_for_status()

    res = resp.json().get('data')
    if res is None:
        raise Exception('returned None, something is not right...')

    return res


def gen_jwt_token(book_id, page=1):
    cur_time = time()
    jwt_to_ken = jwt.encode({
        "p": page,
        "t": int(cur_time) * 1000,
        "b": str(book_id),
        "w": 1000,
        "k": json.dumps(gen_jwt_key(book_id)),
        "iat": int(cur_time)
    }, JWT_SECRET, algorithm='HS256').decode('ascii')
    return jwt_to_ken


def book_info(book_id):
    # url = f"https://lib-nuanxin.wqxuetang.com/v1/read/initread?bid={self.bookid}"  # noqa
    url = f'{URL}/v1/read/initread?bid={book_id}'
    req = httpx.models.Request('GET', URL)
    try:
        resp = SESS.get(url)
        resp.raise_for_status()
    except Exception as exc:
        logger.warning(exc)
        resp = httpx.Response(status_code=499, request=req, content=str(exc).encode())  # noqa

    jdata = resp.json()

    # info = json.loads(r.text)

    # data = info['data']
    # return data['name'], data['canreadpages']

    data = jdata.get('data')
    print(jdata)
    if not data:
        raise Exception('returned None, something is not right...')

    book_info.jdata = jdata

    return data.get('name'), data.get('canreadpages')


def fetch_png(book_id, page=1):
    token = gen_jwt_token(book_id, page)
    url = f'{URL}/page/img/{book_id}/{page}?k={token}'
    headers = {
        'referer': f'{URL}/read/pdf/{book_id}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36 '
        # noqa
    }

    req = httpx.models.Request('GET', URL)

    try:
        resp = SESS.get(url, headers=headers)
        resp.raise_for_status()
    except Exception as exc:
        logger.warning(exc)
        resp = httpx.Response(status_code=499, request=req, content=str(exc).encode())  # noqa

    fetch_png.resp = resp

    try:
        res = resp.content
    except Exception as exc:
        logger.warning(exc)
        return b''

    return res


def main():
    book_id = 3208943
    if not sys.argv[1:]:
        logger.info(' Provide at least a book_id.')
        logger.info(' Using %s to test ' % book_id)
    else:
        book_id = sys.argv[1]

    page = 1
    if not sys.argv[2:]:
        logger.info(' Provide a page number.')
        logger.info(' Using %s to test ' % page)
    else:
        book_id = sys.argv[2]
    logger.info(f' Fetchiing {book_id} {book_info(book_id)} page: {page}')

    res = fetch_png(book_id, page)

    filename = f'{book_id}-{page:03d}.png'

    count = 0
    while Path(filename).exists():
        count += 1
        filename = f'{book_id}-{page:03d}-{count}.png'
        if count > 4:
            break

    Path(filename).write_bytes(res)
    logger.info(f'{filename} saved.')

    if sys.platform in ['win32']:
        os.startfile(f'{filename}')  # type: ignore


if __name__ == '__main__':
    main()
