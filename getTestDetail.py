from functools import partial

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable as pt

from tools import enter, load_cookies, s, headers, Person

bs = partial(BeautifulSoup, features='lxml')


def get_test_deatil(year, term):
    '''
    获取具体的考试安排。
    - year: 查询学年。如 '2017-2018'。
    - term: 查询学期。如 '1'.
    '''
    # 载入
    load_cookies()

    number = Person.number
    nameEncoded = Person.getNameEncoded('utf8')

    print("正在进入考试安排页面...") 
    r = enter('http://jxgl.hdu.edu.cn/xskscx.aspx?xh={0}&xm={1}&gnmkdm=N121604')
    print("开始爬取考试安排...") 

    data = {
        '__EVENTTARGET': 'xqd',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'xnd': year,
        'xqd': term,
    }
    r = s.post('http://jxgl.hdu.edu.cn/xskscx.aspx?xh={0}&xm={1}&gnmkdm=N121604'.format(number, nameEncoded), data=data, headers=headers)
    print(r.text)
    show_table(r.text)
    s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)


def show_table(html):
    '''打印考试安排表。'''
    table = pt(["课程名称", "考试时间", "考试地点", "座位号"])
    for tr in bs(html).find_all('tr')[1:]:
        td = tr.find_all('td')
        l = [x.get_text() for x in td[1:]]
        table.add_row([l[0], l[2], l[3], l[5]])

    print(table.get_string(sortby="考试时间", reversesort=False))
