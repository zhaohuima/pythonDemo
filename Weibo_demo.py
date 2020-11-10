# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/13 14:33
# @File : Weibo_demo.py
# @Software: PyCharm
import requests

headers = {
'Accept': '*/*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Connection': 'keep-alive',
'Content-Length': '269',
'Content-Type': 'application/x-www-form-urlencoded',
'Cookie': '_T_WM=39157744911; WEIBOCN_FROM=1110006030; MLOGIN=0; M_WEIBOCN_PARAMS=uicode%3D10000011%26fid%3D102803; FID=2MGZfNk0BAAMqi4GDY9Fg9XUvx13O5sOXBWxvZ2lu',
'Host': 'passport.weibo.cn',
'Origin': 'https://passport.weibo.cn',
'Referer': 'https://passport.weibo.cn/signin/login?aa=up&entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
}
login_data = {
'username': '***REMOVED***',
'password': '***REMOVED***',
'savestate': '1',
'r': 'https://m.weibo.cn/',
'ec': '0',
'pagerefer': 'https://m.weibo.cn/login?backURL=https%3A%2F%2Fm.weibo.cn%2F',
'entry': 'mweibo',
'wentry': '',
'loginfrom': '',
'client_id': '',
'code': '',
'qq': '',
'mainpageflag': '1',
'hff': '',
'hfp': ''
}

login_res = requests.post('https://passport.weibo.cn/sso/login', data= login_data, headers = headers)
print(login_res.status_code)