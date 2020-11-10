#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/5 13:30
#@File : doubanbook250demo.py
#@Software: PyCharm
import requests
from bs4 import BeautifulSoup
import time
def Getbookname(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    tags = soup.select('div.pl2 a')
    for i in tags:
        name = ''.join(i.text.split())
        link = i['href']
        print(name,link)
url = 'https://book.douban.com/top250?start={}'
urls = [url.format(25 * num) for num in range(10)]
print(urls)
for i in urls:
    Getbookname(i)
    time.sleep(1)