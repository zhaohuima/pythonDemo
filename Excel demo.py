# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/19 11:34
# @File : Excel demo.py
# @Software: PyCharm
from openpyxl import Workbook
#实例化一个工作表
wb = Workbook()
#选择默认的工作表
sheet = wb.active
#给工作表重新命名
sheet.title = '8月考勤表'
#给新创建的wb工作簿的sheet工作表的A1单元格赋值
sheet['A1'] = '小贝'
data = [
  ['姓名', '出勤天数', '迟到次数'],
  ['小贝', 20, 5],
  ['闻闻', 22, 0]
]
for i in data:
    sheet.append(i)
wb.save('考勤系统.xlsx')

