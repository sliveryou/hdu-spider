# -*- coding: UTF-8 -*-

# filename : tools.py
# author by : SliverYou

import sys
from io import BytesIO
from urllib.parse import quote
from http.cookiejar import LWPCookieJar as Cookie

import requests
import pytesseract
from requests.exceptions import RequestException
from PIL import Image

headers = {
    "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}
s = requests.Session()


def enter(url, prompt=True):
    '''
    进入指定的 URL 页面，返回 Response 对象。
    - url: URL 链接。
    - prompt: 设置为 False 时，不打印提示语。 
    '''
    try:
        s.headers[
            'Referer'] = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh={0}'.format(
                Person.number)
        r = s.get(url.format(Person.number, Person.getNameEncoded('gb2312')))
        print("成功进入！") if prompt == True else None
        return r
    except RequestException:
        print("Cookies 失效！进入失败！")
        sys.exit(1)


def load_cookies():
    '''从本地 cookies.text 文件加载 cookies'''
    s.cookies = Cookie()  # 初始化LWPCookieJar
    s.cookies.load('cookies.txt', ignore_discard=True, ignore_expires=True)


def calculate_gpa(grade):
    '''
    根据给定的分数来计算 GPA，并返回 GPA 值。
    - grade: 分数。因为有可能为文字类型和数字类型的分数，所以设定 grade 类型为 str。
    - return: GPA 值。类型为 float。
    '''
    if (grade.isdigit()):
        if (float(grade) > 95):
            gpa = 5.0
        elif (float(grade) >= 60):
            gpa = (float(grade) - 45) / 10
        else:
            gpa = 0
    else:
        dictmap = {'优秀': 5.0, '良好': 4.0, '中等': 3.0, '及格': 2.0, '不及格': 0}
        gpa = dictmap.get(grade)

    return gpa


def download_idcode(url):
    '''指定 URL，下载验证码到本地。'''
    print('\n下载验证码中...')
    try:
        response = s.get(url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save('CheckCode.png')
            print(url, '下载成功！')
            # img.show() # 打开png格式的验证码图片

        s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)
    except RequestException:
        print('验证码获取失败！', url)


def image_read():
    '''对验证码进行识别，并返回识别的结果。'''
    img = Image.open('CheckCode.png')
    img_grey = img.convert('L')  # 灰度化
    threshold = 140
    table = []

    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    img_out = img_grey.point(table, '1')
    text = pytesseract.image_to_string(img_out)  # 结果识别为字符串格式

    return text


class Person:
    '''定义一个 Person 类，用于存储学号和姓名，便于跨文件使用。'''
    name = ''
    number = 0

    @classmethod
    def getNumber(cls):
        return cls.number

    @classmethod
    def getName(cls):
        return cls.name

    @classmethod
    def setName(cls, name):
        cls.name = name

    @classmethod
    def setNumber(cls, number):
        cls.number = number

    @classmethod
    def getNameEncoded(cls, encode):
        return quote(cls.name, encode)
