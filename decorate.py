# -*- coding: UTF-8 -*-

# filename : decorate.py
# author by : SliverYou

def decorate(func, number, quit=True):
    '''
    对所选函数进行装饰（非装饰器），比如：提示输入、检查输入、提醒退出。
    - func: 函数名。
    - number: 学号。
    - quit: quit=False 时，不出现退出提示。
    '''
    while(True):
        year = input('请输入你想要查询的学年（如 2017-2018）：')
        term = input('请输入你想要查询的学期（如 1）：')

        # 检查输入是学期是否为数字，输入的学年指定范围是否为数字
        if term.isdigit() and year[5:].isdigit() and year[:4].isdigit():
            # 判断学期和学年是否是要求范围
            if (0 < int(term) <= 2) is False or (int(year[5:]) - int(year[:4]) == 1) is False:
                print('查询格式输入错误！请重新输入！')
                continue
        else:
            print('查询格式输入错误！请重新输入！')
            continue

        func(number, year, term)

        if quit == True:  
            response = input('按 q 退出查询或其余任意键继续查询：')
            print()
            if response == 'q':
                break
        else:
            break

def judge(choice, n):
    '''
    判断输入格式，确保返回正确的格式。
    - choice: 用户输入的选择编号。
    - n: 选择数字的范围。
    '''
    while(True):
        if choice.isdigit() is False or (0 < int(choice) <= n) is False:
            print('格式输入错误！请输入正确的数字！') 
            choice = input('请重新输入你的选择：')
            print()
        else:
            choice = int(choice)
            break
            
    return choice