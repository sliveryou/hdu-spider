# -*- coding: UTF-8 -*-

# filename : main.py
# author by : SliverYou

import getpass

from getTestDetail import get_test_deatil
from sysLogin import system_login
from getReportCard import get_report_card
from coursesGetAndGuess import courses_get
from selectCourses import select_courses
from decorate import decorate, judge

if __name__ == '__main__':
    #number = 16198709
    #pwd = '1215299941GF1'
    print('(๑•̀ㅂ•́)و✧准备进入数字杭电...')
    number = int(input('请输入学号：'))
    pwd = getpass.getpass('请输入密码（密码不回显）：')
    print('登录中...')
    system_login(number, pwd)

    while(True):
        print('\n>>>>>>>>>功能目录<<<<<<<<<\n')
        print('       1.考试安排查询')
        print('       2.期末成绩查询')
        print('       3.期末成绩预测')
        print('       4.自助选课')
        print('       5.退出')
        print('\n>>>>>>>>>>>结束<<<<<<<<<<<\n')
        choice = input('请输入你的选择（输入数字即可）：')
        print()

        choice = judge(choice, 5)
        if choice == 1:
            decorate(get_test_deatil, number)
        elif choice == 2:
            decorate(get_report_card, number)
        elif choice == 3:
            decorate(courses_get, number, quit=False)
        elif choice == 4:
            select_courses(number)
        elif choice == 5:
            break