#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/8/6 6:19
#@File : zhihudemo.py
#@Software: PyCharm
from selenium import webdriver
import time
browser = webdriver.Chrome()  #路径是chromedriver.exe的存放的位置
browser.get("https://www.zhihu.com/#signin")
time.sleep(5)
#找到用户名输入框
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input').send_keys('13466521691')
#找到密码输入框并输入
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys('***REMOVED***')
#因为要点击图中倒立的文字，暂如法自动化实现，设置5秒时间休眠，手动点击
time.sleep(5)
#点击登录按钮登陆
browser.find_element_by_class_name('Button SignFlow-submitButton Button--primary Button--blue').click()
browser.f
#browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("********") #帐号
# browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("********") #密码
# browser.find_element_by_id("captcha").send_keys(input('请输入验证码：'))
# browser.find_element_by_css_selector(".view-signin button.sign-button").click() #登录
# browser.quit()