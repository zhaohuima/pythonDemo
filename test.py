#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/5 16:26
#@File : test.py
#@Software: PyCharm
import requests
from bs4 import BeautifulSoup

headers = {
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}
res = requests.get('https://book.douban.com/top250', headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
tags = soup.select('div.pl2 a')
for i in tags:
  book_name = i.text
  book_link = i['href']
  print(book_name, book_link)