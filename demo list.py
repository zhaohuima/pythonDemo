#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/7/14 15:27
#@File : demo list.py
#@Software: PyCharm
from typing import List

students: List[str] = [
    'mazhaohui, ',
    'mahaorui, ',
    'zhanghaina',
    'zhanghaipeng',
    'zhanghaiyun',
    'mazhaohui, '
]

students_score = [
    50,
    70,
    80,
    90,
    47,
    100
]

zipped = zip(students, students_score)
students_zipped = list(zipped)
print(students_zipped)