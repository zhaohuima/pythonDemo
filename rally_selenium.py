# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/9 16:40
# @File : rally_selenium.py
# @Software: PyCharm
# 尝试用Selenium 来登陆rally并获取数据 ‘https://rally1.rallydev.com/slm/login.op’
# 导入Selenium, time, bs4
from selenium import webdriver
import time
from bs4 import BeautifulSoup
# 创建一个chrome browser 实例
browser = webdriver.Chrome()
# 打开rally登陆页面
browser.get('https://rally1.rallydev.com/slm/login.op')
# 输入用户名和密码，点击登陆按钮
id_text = browser.find_element_by_id('j_username')
id_text.send_keys('zhaohui.ma@elekta.com')
password_text = browser.find_element_by_id('j_password')
password_text.send_keys('***REMOVED***')
login_button = browser.find_element_by_id('login-button')
login_button.click()
browser.get('https://rally1.rallydev.com/#/263124428812d/iterationstatus')
# <button class="smb-Button smb-Button--secondary smb-Button--xs smb-Button--iconOnly" tabindex="0" type="button"><div class="smb-Button-contents"><span class="smb-Button-icon smb-Button-icon--center"><svg aria-hidden="false" class="smb-SvgIcon smb-SvgIcon--export" focusable="false" role="img" viewBox="0 0 16 16" style="height: 1.6rem; width: 1.6rem;"><title>Import/Export</title><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><rect x="0" y="0" width="16" height="16"></rect><path d="M8,13.3333333 L14,13.3333333 L14,6 L12.6666667,6 L12.6666667,4.66666667 L14,4.66666667 C14.7363797,4.66666667 15.3333333,5.26362033 15.3333333,6 L15.3333333,13.3333333 C15.3333333,14.069713 14.7363797,14.6666667 14,14.6666667 L8,14.6666667 L2,14.6666667 C1.26362033,14.6666667 0.666666667,14.069713 0.666666667,13.3333333 L0.666666667,6 C0.666666667,5.26362033 1.26362033,4.66666667 2,4.66666667 L3.33333333,4.66666667 L3.33333333,6 L2,6 L2,13.3333333 L8,13.3333333 Z M8.66666667,10 L7.33333333,10 L7.33333333,3.89794784 L6.11645058,5.13811538 C5.86104707,5.39840598 5.44695615,5.39840598 5.19155264,5.13811538 C4.93614912,4.87782478 4.93614912,4.45581032 5.19155264,4.19551972 L8,1.33333333 L10.8084474,4.19551972 C11.0638509,4.45581032 11.0638509,4.87782478 10.8084474,5.13811538 C10.5530438,5.39840598 10.1389529,5.39840598 9.88354942,5.13811538 L8.66666667,3.89794784 L8.66666667,10 Z" fill="currentColor"></path></g></svg></span></div></button>
up_button = browser.find_element_by_xpath(by = by.XPATH, value = '/html/body/div[1]/div/div[4]/div/div/div[3]/div[1]/div/div/div/div[2]/div[4]/div/div/span/button')
up_button.click()
download_button = browser.find_element_by_partial_link_text('Download CSV')


# 选择'keystone'team
# 选取Pi3.4的story并输出