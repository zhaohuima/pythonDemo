# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/9 6:51
# @File : sohudemo.py
# @Software: PyCharm
import requests
from bs4 import BeautifulSoup
import xlsxwriter

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}
res = requests.get('https://www.sohu.com/a/211030894_266715', headers = headers)
soup = BeautifulSoup(res.text, 'html.parser')

article = soup.select('.article#mp-editor p img')
image_link_list = []
for i in article:
    image_link = i['src']
    image_link_list.append(image_link)

for i in image_link_list:
    res_img = requests.get(i, headers = headers)
    with open('agileimg.doc', 'ab') as f:
        f.write(res_img.content)
    print(i + '打印完成')


# for i in article:
#     text_sub = ''.join(i.text.split())
#     print(text_sub)