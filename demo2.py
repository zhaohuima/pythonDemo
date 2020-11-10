#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/14 17:40
#@File : demo1.py
#@Software: PyCharm
'''
print("标准化输出字符串")
'''
'''
#格式化输出
age = 18
name = "geoffrey"
print("我的年龄是%d岁"%age)
print("我的名字是%s,我的国籍是%s"%(name, "China"))
print("我的名字是%s"%name)
print("aaa","bbb","ccc")
print("www","baidu","com",sep=".")
print("hello, python", end="\t")
print("hello, python", end="\n")
print("end")
'''
'''
password = input("请输入密码")
print("您输入的密码是:",password)
'''

# a = 10
a = input("输入")
print(type(a))
b = int(a)
print(type(b))
print("请输入一个数字:%d"%b)

'''
a = int("150")
b = a + 100
print(b)
print(type(a))
print(type(b))
'''