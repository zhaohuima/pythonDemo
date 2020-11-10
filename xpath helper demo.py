#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/23 10:38
#@File : xpath helper demo.py
#@Software: PyCharm

#测试xpath helper的使用
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('http://www.baidu.com/')
element_search_text = driver.find_elements_by_xpath(/html/body/div[@id='wrapper']/div[@id='head']/div[@id='head_wrapper']/div[@class='s_form s_form_nologin']/div[@class='s_form_wrapper soutu-env-nomac soutu-env-index']/form[@id='form']/span[@class='bg s_ipt_wr quickdelete-wrap ipthover']/input[@id='kw'])