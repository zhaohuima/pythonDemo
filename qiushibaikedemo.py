#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/8 7:00
#@File : qiushibaikedemo.py
#@Software: PyCharm
import requests
from bs4 import BeautifulSoup
import time
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36'
}
res = requests.get('https://www.qiushibaike.com/text/', headers = headers)
soup = BeautifulSoup(res.text, 'html.parser')
feed = soup.find_all('div.content')
print(feed)
