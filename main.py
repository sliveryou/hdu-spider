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
from tools import Person


if __name__ == '__main__':
    print('(๑•̀ㅂ•́)و✧准备进入数字杭电...')
    number = int(input('请输入学号：'))
    pwd = getpass.getpass('请输入密码（密码不回显）：')
    print('登录中...')
    name = system_login(number, pwd)
    print('你好，{} :）'.format(name))

    Person.setName(name)
    Person.setNumber(number)

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
            decorate(get_test_deatil)
        elif choice == 2:
            decorate(get_report_card)
        elif choice == 3:
            decorate(courses_get, quit=False)
        elif choice == 4:
            select_courses()
        elif choice == 5:
            break
