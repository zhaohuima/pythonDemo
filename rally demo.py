# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/8 14:01
# @File : rally demo.py
# @Software: PyCharm
import requests
from bs4 import BeautifulSoup
headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36'
}

login_data = {

'username': 'zhaohui.ma@elekta.com',
'password': 'CNMAZHA2',
'initialRequest': ''
}

r = requests.post('https://elekta.mastercontrol.com/elekta/restapi/identity/authentication/login', headers=headers, data=login_data)
print(r.status_code)
res = requests.get('https://elekta.mastercontrol.com/elekta/index.cfm?infocard_id=4GYURLD6WVBCHLSTLV#/', headers = headers, cookies = r.cookies)
print(res.status_code)
soup = BeautifulSoup(res.text, 'html.parser')
print(soup)