# @Author:Zhaohui.Ma
# -*- coding = utf-8 -*-
# @Time : 2020/8/9 9:47
# @File : Selenium demo.py
# @Software: PyCharm
from selenium import webdriver
import time
# 下面是登陆后发布评论的代码
# browser = webdriver.Chrome()
# browser.get('https://wpblog.x0y1.com/wp-login.php')
# time.sleep(2)
# # 找到账户文本框
# login_text = browser.find_element_by_class_name('input')
# # 传用户ID给登陆按钮
# login_text.send_keys('codetime')
# # 找到密码文本框
# password_text = browser.find_element_by_id('user_pass')
# # 传密码给密码文本框
# password_text.send_keys('shanbay520')
# # 找到登陆按钮
# login_button = browser.find_element_by_id('wp-submit')
# # 点击登陆按钮
# login_button.click()
# # 打开评论页面
# browser.get('https://wpblog.x0y1.com/?p=34')
# # 找到输入评论的文本框
# comment_text = browser.find_element_by_id('comment')
# # 传“需要发表的评论“给文本框
# comment_text.send_keys('需要发表的评论')
# # 找到发布按钮
# submit_button = browser.find_element_by_id('submit')
# # 点击发布按钮发布
# submit_button.click()
# #browser.quit()

# 下面是搜索'python'的代码
# 创建一个浏览器实例
browser = webdriver.Chrome()
# 打开浏览器，进入搜索页面
browser.get('https://wpblog.x0y1.com/')
# 找到搜索框
# <input type="search" id="search-form-1" class="search-field" placeholder="搜索…" value="" name="s">
search_text = browser.find_element_by_id('search-form-1')
# 在搜索框中输入‘python’
search_text.send_keys('python')
# 找到搜索按钮
# <button type="submit" class="search-submit"><svg class="icon icon-search" aria-hidden="true" role="img"> <use href="#icon-search" xlink:href="#icon-search"></use> </svg><span class="screen-reader-text">搜索</span></button>
search_button = browser.find_element_by_class_name('search-submit')
# 点击搜索按钮
#time.sleep(2)
search_button.click()
# 通过class name找到标题列表
titles = browser.find_elements_by_class_name('entry-title')
# 用循环打印每一个title的text
print(titles)
for title in titles:
    print(title.text)
# 退出浏览器
browser.quit()