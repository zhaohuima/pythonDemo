#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/19 11:49
#@File : export master control.py
#@Software: PyCharm

#这个例子用于练习把master control中文档的review/approve信息抓取出来


headers = {"User - Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"}

import time
import json
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
driver = webdriver.Chrome()


driver.get('https://elekta.mastercontrol.com/elekta/login/index.cfm?initialRequest=%2Felekta%2Findex.cfm#/hubs/my-mastercontrol')
element_username = driver.find_element_by_id('username')
element_username.send_keys('zhaohui.ma@elekta.com')
#element_loginbutton = driver.find_elements_by_id('loginButton')
element_loginbutton = driver.find_element_by_xpath('//*[@id="loginButton"]')
element_loginbutton.click()
time.sleep(30)
cookies = driver.get_cookies()
print(cookies)

f1 = open('cookie.txt', 'w')
f1.write(json.dumps(cookies))
f1.close

f1 = open('cookie.txt')
cookie = f1.read()
cookie =json.loads(cookie)
for c in cookie:
    driver.add_cookie(c)
# # 刷新页面
driver.refresh()


urlE014074 = 'https://elekta.mastercontrol.com/elekta/index.cfm?packet_id=7SOPUPG4XRGZDMYW7T&tracking=true#/'
with request.urlopen(urlE014074) as file:
    data = file.read().decode('utf-8')

with open("E014074.txt", "w") as file2:
    datastr = str(data)
    file2.write(datastr)

'''
diver.get('http://www.baidu.com/')
element_keyword = driver.find_element_by_id('kw')
element_keyword.send_keys('agile')
element_keyword_search = driver.find_element_by_id('su')
element_keyword_search.click()
'''