#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/26 10:32
#@File : csdn login.py
#@Software: PyCharm
import requests
from urllib import request
from bs4 import BeautifulSoup
cookie = 'uuid_tt_dd=10_19288668560-1593138937464-122653; dc_session_id=10_1593138937464.815944; c_first_ref=default; c_first_page=https%3A//blog.csdn.net/LEE18254290736/article/details/53967588; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1593137908,1593138179,1593138523,1593138551; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_19288668560-1593138937464-122653!1788*1*PC_VC!5744*1*weixin_45434493; dc_sid=1dcd5a72c5e828b22987e65103d1ccf2; __gads=ID=b796585feeb55756:T=1593138938:S=ALNI_MYVykXPrA1YHjfKEZ4SpZ9tyHqULw; SESSION=f6b188ff-682e-4a13-8ba5-881cf9c8a86d; c_ref=https%3A//blog.csdn.net/godot06/article/details/81240113; UserName=weixin_45434493; UserInfo=6f856e24df784d7ab90746d417a0a33a; UserToken=6f856e24df784d7ab90746d417a0a33a; UserNick=%E9%BA%BB%E6%9C%9D%E8%BE%89; AU=F28; UN=weixin_45434493; BT=1593139130388; p_uid=U000000; TY_SESSION_ID=6e9f3a3f-1ddd-428e-8113-3954ff7e22e8; c_page_id=https%3A//www.csdn.net/; dc_tos=qcii0z; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1593139140; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22weixin_45434493%22%2C%22scope%22%3A1%7D%7D; announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Fmarketing.csdn.net%252Fp%252F00839b3532e2216b0a7a29e972342d2a%253Futm_source%253D618%2522%252C%2522announcementCount%2522%253A0%252C%2522announcementExpire%2522%253A3600000%257D'
header = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
'Connection': 'keep-alive',
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Cookie': cookie,
'referer': 'https://blog.csdn.net/weixin_37719937'
}
url = 'https://me.csdn.net/api/user/show' # csdn 个人中心中，加载名字的js地址
seesion = requests.session()
response = seesion.get(url,headers=header)
#response.coding="gbk"
wbdata = response.text
print("正在打开请求")
print(response.url)
print()
soup = BeautifulSoup(wbdata,'lxml')
print(soup)

