#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/7/23 15:44
#@File : for cicle demo.py
#@Software: PyCharm
# 输出：[1, 9, 25, 49, 81]
y = [i * i for i in range(1,10) if i % 2 == 1]
print(y)