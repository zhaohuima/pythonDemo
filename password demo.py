#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/7/10 19:09
#@File : password demo.py
#@Software: PyCharm
def guess_password(num):
  if num <= 1 or num >= 999999:
    print('请输入1-999999之内的数')
  elif num == 666:
    print('哼，以为喊我六六六我就能给你开电脑了吗？')
  elif num == 768145:
    print('密码猜对了，玩一会就去学习吧')
  else:
    print('密码不正确，快去学习吧')
result = int(input('刘星猜测的电脑密码是？：'))
guess_password(result)