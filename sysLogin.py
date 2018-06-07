import re
import sys
import hashlib
from functools import partial
from http.cookiejar import LWPCookieJar as Cookie

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from tools import s, headers

bs = partial(BeautifulSoup, features='lxml')

def system_login(number, pwd):
    '''
    给定学号和密码，登录 HDU 选课系统。
    - number: 学号。
    - pwd: 密码。
    '''
    s.cookies = Cookie() # 初始化 LWPCookieJar
    try:
        html = s.get("http://cas.hdu.edu.cn/cas/login", headers=headers, timeout=4)
    except RequestException:
        print("请求超时！请检查网络后再次尝试！")
        sys.exit(1)

    # 表单信息
    data = {
        'encodedService': 'http%3a%2f%2fi.hdu.edu.cn%2fdcp%2findex.jsp',
        'service': 'http://i.hdu.edu.cn/dcp/index.jsp',
        'serviceName': 'null',
        'loginErrCnt': '0',
        'username': str(number),
        'password': hashlib.md5(pwd.encode('utf-8')).hexdigest(),  # 密码要经过 md5 哈希后提交
        'lt': bs(html.text).select('input[name="lt"]')[0]['value']  # lt 是一个不断改变的值，所以需要在网页中获取它的值
    }

    # 数字杭电网页版登录
    try:
        html = s.post("http://cas.hdu.edu.cn/cas/login", headers=headers, data=data)  # 提交表单
        url = re.search(r'<a href="(.*)">', html.text)  # 重定向
        s.get(url.group(1), headers=headers)
        html = s.get("http://i.hdu.edu.cn/dcp/forward.action?path=/portal/portal&p=wkHomePage", headers=headers)
    except RequestException:
        print("密码错误！请尝试重新登录！")
        sys.exit(1)

    # 选课系统登录
    html = s.get('http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/default.aspx')
    url = re.search(r'<a href="(.*)">', html.text)
    s.get(url.group(1), headers=headers)

    # 获取姓名
    try:
        html = s.get('http://jxgl.hdu.edu.cn/xs_main.aspx?xh={0}'.format(number))
        name = bs(html.text[2000:4000]).select('div[class="info"] ul li em span')[0].text
        s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True) # 将 cookies 存储到本地
        print('登录成功！')
    except:
        print("密码错误！请尝试重新登录！")
        sys.exit(1)

    return name[:-2]
