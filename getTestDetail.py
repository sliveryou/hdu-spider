from functools import partial

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable as pt

from tools import enter, load_cookies, s, headers

bs = partial(BeautifulSoup, features='lxml')

def get_test_deatil(number, year, term):
    '''
    获取具体的考试安排。
    - number: 学号。
    - year: 查询学年。如 '2017-2018'。
    - term: 查询学期。如 '1'.
    '''
    # 载入
    load_cookies()
    print("正在进入考试安排页面...") 
    r = enter('http://jxgl.hdu.edu.cn/xskscx.aspx?xh={0}&xm=%CD%F5%D3%EA%EA%BF&gnmkdm=N121604', number)
    print("开始爬取考试安排...") 

    data = {
        '__EVENTTARGET': 'xqt',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'xnd': year,
        'xqd': term,
    }
    r = s.post('http://jxgl.hdu.edu.cn/xskscx.aspx?xh={0}&xm=%u738b%u96e8%u6615&gnmkdm=N121604'.format(number), data=data, headers=headers)

    table = pt(["课程名称", "考试时间", "考试地点", "座位号"])
    for tr in bs(r.text).find_all('tr')[1:]:
        td = tr.find_all('td')
        l = [ x.get_text() for x in td[1:] ]
        table.add_row([l[0], l[2], l[3], l[5]])

    print(table.get_string(sortby="考试时间", reversesort=False))
    s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)
