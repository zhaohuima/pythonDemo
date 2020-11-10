#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/7 15:01
#@File : dongtaidemo.py
#@Software: PyCharm
import requests
from bs4 import BeautifulSoup
import json

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}
res = requests.get('http://icloudy.cechina.cn/api/LoadArticleHandler.ashx?pageIndex=2&pageSize=12&siteId=7', headers = headers)
data = res.json()['list']
for i in range(12):
    title = data[i]['Title']
    author = data[i]['Author'] + '\n'
    print(title,author)
    with open('test.txt', 'a') as f:
        f.write(title)
        f.write(author)

