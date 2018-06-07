# -*- coding: UTF-8 -*-

# filename : coursesGetAndGuess.py
# author by : SliverYou

import os
import shutil
from functools import partial

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable as pt

from tools import s, headers, enter, load_cookies, calculate_gpa, Person
from decorate import judge

bs = partial(BeautifulSoup, features='lxml')

def courses_get(year, term):
    '''
    获取本学期所有已选课程，并将其写入 courses_results.txt 文件
    - year: 查询学年。如 '2017-2018'.
    - term: 查询学期。如 '2'。
    '''
    load_cookies()

    number = Person.number
    nameEncoded = Person.getNameEncoded('utf8')

    print("正在进入选课情况查询页面...") 
    r = enter('http://jxgl.hdu.edu.cn/xsxkqk.aspx?xh={0}&xm={1}&gnmkdm=N121115')
    print("开始爬取选课情况信息...") 

    data = {
        '__EVENTTARGET': 'ddlXQ',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': bs(r.text).select('input[name="__VIEWSTATE"]')[0]['value'],
        '__EVENTVALIDATION': bs(r.text).select('input[name="__EVENTVALIDATION"]')[0]['value'],
        'ddlXN': year,
        'ddlXQ': term
    }
    r = s.post('http://jxgl.hdu.edu.cn/xsxkqk.aspx?xh={0}&xm={1}&gnmkdm=N121115'.format(number, nameEncoded), data=data, headers=headers)

    table = pt(['选课课号', '课程名称', '教师姓名', '学分', '上课时间'])
    courses_results = []

    for tr in bs(r.text).find_all('tr')[1:]:
        td = tr.find_all('td')
        L = [ x.get_text() for x in td ]
        table.add_row([L[0][14:22], L[1], L[4], L[5], L[7]])
        courses_results.append(L[0][14:22] + ' ' +  L[1] + ' ' + L[4] + ' ' + L[5] + '\n')  # 记录要写入文件的信息

    s.cookies.save('cookies.txt', ignore_discard=True, ignore_expires=True)

    print('本学期已选课程如下所示：')
    print(table)
    print('正在将信息写入文件(courses_results.txt)...')

    # 创建一个 results/ 文件夹，用于存放文件结果
    try:
        os.mkdir('results/')
    except FileExistsError:
        pass  # 已存在文件夹的话，就忽略 FileExistsError 异常

    with open('results/courses_results.txt', 'wt') as f:
        for result in courses_results:
            f.write(result)  # 遍历列表，一行一行写入信息
        print('信息写入成功！请到相应目录打开 results/ 文件夹并在 courses_guess.txt 文件中写入推测成绩！')
        f.close()

    print('开始期末成绩预测：')

    while True:
        print('\n*#*#*#*#*#*#*#*#*\n')
        print(' 1.获取推测成绩表')
        print(' 2.退出')
        print('\n*#*#*#*#*#*#*#*#*\n')
        c = input('请输入你的选择（输入数字即可）：')
        print()
        c = judge(c, 2)
        if c == 1:
            courses_guess()
        elif c == 2:
            break


def courses_guess():
    '''
    注：要先将 courses_results.txt 文件的内容复制到 courses_guess.txt 文件中，
    然后将猜测成绩填入 courses_guess.txt文 件后计算猜测 GPA。
    '''
    if not os.path.exists('results/courses_guess.txt'):
        print('请先将 courses_results.txt 文件的内容复制到 courses_guess.txt 文件中，并在末尾写好推测分数哦~')
        print('PS：如果文件不存在请先创建 courses_guess.txt 文件~')
        # 防止人懒，还是直接复制一份文件好了
        shutil.copy('results/courses_results.txt', 'results/courses_guess.txt')
        return False

    with open('results/courses_guess.txt', 'rt') as f:
        guess = []
        for x in f.readlines():
            line = x[:-1].split(' ')

            # 添加预测分数时，请确保分数后没有空格等空字符
            if len(line) != 5:
                print('请在 courses_guess.txt 文件末尾写好推测分数哦~')
                print('如：A0714040 概率论与数理统计 宫改云 3.0 94')
                return False

            guess.append(line)

        credit, sum, credit_notc, sum_notc = 0, 0, 0, 0
        table = pt(['选课课号', '课程名称', '教师姓名', '学分', '推测分数', '推测绩点'])  # 初始化表头

        for x in guess:
            gpa = calculate_gpa(x[4])
            x.append(gpa) # 插入GPA数据
            table.add_row(x)
            credit = credit + float(x[3])
            sum = sum + float(x[3]) * gpa

            if(x[0][0] != 'C'): # 计算不含C类课的学分绩点
                credit_notc = credit_notc + float(x[3])
                sum_notc = sum_notc + float(x[3]) * gpa

        # 打印信息
        print('推测成绩表如下：')
        print(table.get_string(sortby="推测绩点", reversesort=True))
        print("本学期所修学分为（含c类课）：{0}".format(credit))
        print("本学期所修学分为（不含c类课）：{0}".format(credit_notc))
        print("本学期平均学分绩点为（含c类课）：{0}".format(sum / credit))
        print("本学期平均学分绩点为（不含c类课）：{0}".format(sum_notc / credit_notc))
        