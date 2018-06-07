# -*- coding: UTF-8 -*-

# filename : coursesGetAndGuess.py
# author by : SliverYou

import os
import re
from functools import partial

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable as pt

from tools import s, headers, enter, load_cookies, download_idcode, image_read, Person
from decorate import judge

bs = partial(BeautifulSoup, features='lxml')

hidXNXQ = '2017-20182' # 如果现在是 2017-2018 年度第1学期，这时候要选的课是下一个学期的课，所以学期应为第2学期，即 '2017-20182'
                       # 如果现在是 2017-2018 年度第2学期，这时候要选的课是下一个学年下一个学期，应为 '2018-20191'，以此类推


def look_courses(html):
    '''
    打印当前已选公选课课程。
    html: 选课页面的 HTML 字符串。
    '''
    table = bs(html).find_all('table', class_='datelist')[1]
    table_has = None

    for i, tr in enumerate(table.find_all('tr')):
        td = tr.find_all('td')
        L = [ x.get_text() for x in td ]
        if i == 0:
            table_has = pt(['课程编号'] + L[:-1])
        else:
            table_has.add_row([i-1] + L[:-1])

    print('已选课程如下所示：')
    print(table_has)


def get_select_page(number, nameEncoded):
    '''
    进入选课页面，返回此时的 Session 对象 和 Response 对象。
    - number: 学号。
    - nameEncoded: 编码过后的姓名。
    '''
    load_cookies()

    r = enter('http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh={0}&xm={1}&gnmkdm=N121113', prompt=False)

    data = {
        '__EVENTTARGET': 'ddl_kcgs',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'ddl_kcxz': '',	
        'ddl_ywyl': '有'.encode('gb2312'),
        'ddl_kcgs': '',	
        'ddl_xqbs': '1',
        'ddl_sksj': '',	
        'TextBox1': '',
        'Button2': '确定'.encode('gb2312'),	
        'txtYz': '',	
        'hidXNXQ': hidXNXQ
    }

    r = s.post('http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh={0}&xm={1}&gnmkdm=N121113'.format(number, nameEncoded), data=data, headers=headers)    
    return s, r


def go_to_select(xk, s, r):
    '''
    提交表单，完成选课。
    - xk: 选课编号。
    - s: Session 对象。
    - r: Response 对象。

    - return: s, r, result: 提交表单后的 Session 对象, 提交表单后的 Response 对象和验证码校验结果。
    '''
    number = Person.number
    nameEncoded = Person.getNameEncoded('utf8')

    download_idcode('http://jxgl.hdu.edu.cn/CheckCode.aspx')  # 下载验证码
    idcode = image_read()  # 返回验证码识别结果
    print("识别结果为：", idcode, '\n',sep='')

    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'ddl_kcxz': '',	
        'ddl_ywyl': '有'.encode('gb2312'),
        'ddl_kcgs': '',	
        'ddl_xqbs': '1',
        'ddl_sksj': '',	
        'TextBox1': '',
        xk: 'on',	
        'txtYz': idcode,	
        'Button1': '  提交  '.encode('gb2312'),
        'hidXNXQ': hidXNXQ
    }

    s.cookies.load('cookies.txt', ignore_discard=True, ignore_expires=True)
    r = s.post('http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh={0}&xm={1}&gnmkdm=N121113'.format(number, nameEncoded), data=data, headers=headers)

    try:
        result = re.search(".*?alert\('(.*?)！！.*?", r.text[:50], re.S).group(1) # 查看是否有 alert 提醒，如果有返回值，说明验证码校验失败
    except AttributeError:
        # re.search 失败，说明验证么校验成功
        result = 'Yes'
        print('验证码校验成功！\n')

    return s, r, result


def select_courses():
    '''
    进入选课页面，进行选课操作。
    '''
    number = Person.number
    nameEncoded = Person.getNameEncoded('utf8')
    
    print("正在进入选课页面...") 
    s, r = get_select_page(number, nameEncoded)
    print("开始爬取选课信息...") 

    table = pt(["编号", "课程名称", "课程代码", "教师姓名", "上课时间", "学分", "起始结束周", "容量", "余量", "课程归属", "课程性质"])
    i = 0

    for tr in bs(r.text).find_all('tr')[1:]:
        td = tr.find_all('td')
        L = [ x.get_text() for x in td ]
        l = L[2:6] + [L[7]] + L[9:14]

        if '退选' in l:
            # 包含退选关键字的是已选课程，不能放在选课列表。
            break

        table.add_row([i] + l)  # 记录编号和可选课程的信息
        i = i + 1

    print('所有可选课程如下所示：')
    print(table)

    while True:
        print('\n*#*#*#*#*#*#*#*#*\n')
        print(' 1.按课程编号选课')
        print(' 2.按课程名称选课')
        print(' 3.查看已选课程')
        print(' 4.退选已选课程')
        print(' 5.退出')
        print('\n*#*#*#*#*#*#*#*#*\n')

        choice = input('请输入你的选择（输入数字即可）：')
        print()

        choice = judge(choice, 5)  # 判断输入格式，确保返回正确的格式。

        if choice == 1:
            num = input('请输入将选课程的编号：')

            while num.isdigit() is False:
                print('格式输入错误！请输入正确的数字！') 
                num = input('请再次输入将选课程的编号：')

            num = int(num)

            # 检验提交的表单，发现表单要提交的数据是显示标号数+2，所有要将编号数+2后再提交
            if 0 <= num < 8:
                xk =  'kcmcGrid$ctl0{}$xk'.format(num+2)
            elif 8 <= num < i:
                xk =  'kcmcGrid$ctl{}$xk'.format(num+2)
            s, r, result = go_to_select(xk, s, r)

            while result == '验证码不正确':
                print('验证码校验失败！正在重新提交...')
                s, r = get_select_page(number, nameEncoded)
                s, r, result = go_to_select(xk, s, r)

            print('φ(≧ω≦*)♪选课中...')
            print('......')
            print('成功完成选课٩(๑>◡<๑)۶！\n')
            look_courses(r.text)
            s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)
            continue

        elif choice == 2:
            # 时间有限，还未研发该功能
            break

        elif choice == 3:
            look_courses(r.text)
            s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)
            continue

        elif choice == 4:
            print('正在进行退课操作！请谨慎操作！（可按q退出退课操作）')
            num = input('请输入需要退选的课程编号：')

            if num == 'q':
                continue

            num = input('请再次确认需要退选的课程编号：')  # 退课需谨慎，所以需要重复两次确认操作
             
            while num.isdigit() is False:
                print('格式输入错误！请输入正确的数字！') 
                num = input('请再次输入需要退选课程的编号：')

            num = int(num)

            if 0 <= num < 8:
                tk =  'DataGrid2$ctl0{}$ctl00'.format(num+2)
            elif 8 <= num < i:
                tk =  'DataGrid2$ctl{}$ctl00'.format(num+2)

            data = {
                '__EVENTTARGET': tk,
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
                '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
                'ddl_kcxz': '',	
                'ddl_ywyl': '有'.encode('gb2312'),
                'ddl_kcgs': '',	
                'ddl_xqbs': '1',
                'ddl_sksj': '',	
                'TextBox1': '',	
                'txtYz': '',	
                'hidXNXQ': hidXNXQ
            }

            r = s.post('http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh={0}&xm={1}&gnmkdm=N121113'.format(number, nameEncoded), data=data, headers=headers)

            print('\nφ(≧ω≦*)♪退课中...')
            print('......')
            print('成功完成退课٩(๑>◡<๑)۶！\n')

            look_courses(r.text)
            s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)
            continue

        elif choice == 5:
            break