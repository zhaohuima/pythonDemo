#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/23 11:17
#@File : from Myapp to master control.py
#@Software: PyCharm
from urllib import request
from selenium import webdriver
headers = {"User - Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"}
driver = webdriver.Chrome()

driver.get('https://account.activedirectory.windowsazure.com/r?whr=elekta.com#/applications')
element_mastercontrol = driver.find_elements_by_xpath('/html/body/main[@class='container']/div[@class='container-no-padding-horiz apps-index-page']/div[@class='row'][2]/div[@class='col-xs-12 col-sm-12 col-md-9']/div[@class='row']/div[@class='col-xs-12 col-sm-4 apptile tile noselect ng-not-empty ng-valid col-md-4'][14]/div[@class='col-xs-12 tile-body no-padding-horiz']/img[@class='app-icon']/@src')
element_mastercontrol.click()
