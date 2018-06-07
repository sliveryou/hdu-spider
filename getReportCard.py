# -*- coding: UTF-8 -*-

# filename : getReportCard.py
# author by : SliverYou

from functools import partial

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable as pt

from tools import s, headers, enter, load_cookies, calculate_gpa, Person

bs = partial(BeautifulSoup, features='lxml')


def get_report_card(year, term):
    '''
    进入成绩页面并打印成绩单，包括分数，GPA等。
    - year: 查询学年。如 '2017-2018'.
    - term: 查询学期。如 '2'。
    '''
    load_cookies()

    number = Person.number
    nameEncoded = Person.getNameEncoded('utf8')

    print("正在进入选课系统成绩页面...") 
    r = enter('http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh={0}&xm={1}&gnmkdm=N121605')
    print("开始爬取成绩单...") 

    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'ddlxn': year,
        'ddlxq': term,
        'btnCx': ' 查  询 '
    }
    r = s.post('http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh={0}&xm={1}&gnmkdm=N121605'.format(number, nameEncoded), data=data, headers=headers)
    s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)

    show_table(r.text, year, term)
        

def show_table(html, year, term):
    '''打印指定学年和学期的成绩单。'''
    credit, sum, credit_notc, sum_notc = 0, 0, 0, 0  # 初始化学分、绩点、去 C 类课学分和去 C 类课绩点
    table = pt(["课程代码", "课程名称", "课程性质", "课程归属", "学分", "成绩", "补考成绩", "是否重修", "开课学院", "备注", "补考备注", "单科绩点"])  # 初始化表头
    Fail = []  # 初始化补考列表

    for tr in bs(html).find_all('tr')[4:]:
        td = tr.find_all('td')
        L = [ str(x) for x in td[2:] ]
        datas = []

        for x in L:
            if(x[4:-5] != '\xa0'):  # 判断数据是否为空
                datas.append(x[4:-5])
            elif(x[4:-5] == '\xa0'):
                datas.append('无')

        gpa = calculate_gpa(datas[5])  # 计算 GPA 的值

        if gpa == 0:  # 如果该科目不及格，就将科目信息记录到 Fail 列表
            Fail.append((datas[1], datas[0], datas[6], datas[4])) #补考课程名称、课程代码、补考成绩和课程学分

        datas.append(gpa)  # 插入 GPA 数据到 datas 列表最后一位
        table.add_row(datas)  # 插入一行到 table 中
        credit = credit + float(datas[4])
        sum = sum + float(datas[4]) * gpa

        if(datas[0][0] != 'C'):  # 计算不含 C 类课的学分绩点
            credit_notc = credit_notc + float(datas[4])
            sum_notc = sum_notc + float(datas[4]) * gpa

    # 打印信息
    print("{0}学年第{1}学期成绩表如下：".format(year, term))
    print(table.get_string(sortby="单科绩点", reversesort=True))  # 将表的信息根据单科绩点列来排序
    print("本学期所修学分为（含c类课）：{0}".format(credit))
    print("本学期所修学分为（不含c类课）：{0}".format(credit_notc))
    print("本学期平均学分绩点为（含c类课）：{0}".format(sum / credit))
    print("本学期平均学分绩点为（不含c类课）：{0}".format(sum_notc / credit_notc))

    if Fail:  # 如果补考列表不为空，说明存在某科目不及格现象
        print('\n本学期不及格科目数量：{0}'.format(len(Fail)))

        for x in Fail:
            if x[2] == '无':
                print('{} 补考成绩还未公布，可稍后再次查询~'.format(x[0]))
                continue

            elif float(x[2]) >= 60:
                print('{} 补考成功ヾ(^▽^ヾ)！'.format(x[0]))
                if x[1][0] != 'C':
                    sum = sum + float(x[3]) * calculate_gpa(x[2])
                    sum_notc = sum_notc + float(x[3]) * calculate_gpa(x[2])

                elif x[1][0] == 'C':
                    sum = sum + float(x[3]) * calculate_gpa(x[2])

            elif float(x[2]) < 60:
                print('{} 补考失败_(:з」∠)_...你懂的...'.format(x[0]))

        print("补考后本学期平均学分绩点为（含c类课）：{0}".format(sum / credit))
        print("补考后本学期平均学分绩点为（不含c类课）：{0}".format(sum_notc / credit_notc))
        