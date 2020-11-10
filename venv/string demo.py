#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/7/30 9:22
#@File : string demo.py
#@Software: PyCharm
def print_string(name, age, city):
    print('我叫%s, 今年%d, 来自%s'%(name, age, city))
print_string('麻花儿',18,'唐山')
print_string('海娜姐',16,'丹东')
import time
print(time.time())
print(time.ctime())
import datetime
print(datetime.datetime.now() - datetime.timedelta(days=5))
import random
print(random.random())
print(random.randint(0,6))
print(random.uniform(0,8))
print(random.choice(['校长','老师','同学']))