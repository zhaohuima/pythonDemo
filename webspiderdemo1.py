#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/3 21:57
#@File : webspiderdemo1.py
#@Software: PyCharm
from typing import TextIO

import requests
from bs4 import BeautifulSoup
headers = {
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}
response = requests.get('https://book.douban.com/top250', headers = headers)
print(response.encoding)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

tags = soup.select('div.pl2 a')
for i in tags:
  book_name = ''.join(i['title'].split())
  book_link = i['href']
  print(book_name,book_link)
  with open('book_list','a') as file:
    file.write(book_name)


