#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/5 10:55
#@File : douban movie.py
#@Software: PyCharm
import requests
from bs4 import BeautifulSoup
import  time

def movie(url):
  headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
  }
  res = requests.get(url,headers = headers)
  soup = BeautifulSoup(res.text, 'html.parser')
  tags = soup.select('div.hd a')
  for i in tags:
    tags_span = i.find('span', class_ = 'title')
    name = tags_span.text
    link = i['href']
    print(name, link)


url = 'https://movie.douban.com/top250?start={}'
urls = [url.format(num * 25) for num in range(10)]

for i in urls:
  movie(i)
  time.sleep(1)