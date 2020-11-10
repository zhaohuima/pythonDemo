#@Author:Zhaohui.Ma
#-*- coding = utf-8 -*-
#@Time : 2020/6/26 10:56
#@File : csdn copy to master control.py
#@Software: PyCharm

import requests
from urllib import request
from bs4 import BeautifulSoup
cookie = 'EXPIRETIME=0.25; MCROUTE=mc.; CFTOKEN=0; SAML=; CFID=615c6df3-5704-4129-9263-5746c98fa2d8; TEMPMESSAGEDISPLAYUSERID=CNMAZHA; LASTACTIVITY=26-06-2020_02-58-54; visid_incap_2012038=dBvSd8YMRlWRd4OSPN6dp2y68l4AAAAAQUIPAAAAAABqbxJ/5FIgvCO6MeReMTrF; rxVisitor=1592875595710BBOVL5AF4HMJK85BHEHHVG4DQDIF5UN7; incap_ses_1206_2012038=oGtlQkNDIEnOhphCMZO8EE/m8l4AAAAAMTnUzod6Tz9zWwKD9IOVhw==; incap_ses_1205_2012038=k3KqaVEEfCAh1931rQW5EKPo8l4AAAAAKyb+Ah0wwdiuiEPpMrPAQQ==; visid_incap_1709773=qh/FRnouSpCnGROuQumoH0Xs8l4AAAAAQUIPAAAAAACiM1cn4sU2KSauOQ6QdHRT; incap_ses_431_1709773=fpLkBrbonAJiC1ptPjj7BUXs8l4AAAAAxWkiPT9xtLzuUpW0DEYPmg==; ENTRYPAGE=%2F; source_string=https%3A%2F%2Fwww.google.com.hk%2F; s_fid=1691EAA202C67DC5-21360932CD0284F1; s_cc=true; _ga=GA1.2.1434908911.1592978507; s_vi=[CS]v1|2F7976258515BA32-60000A134BED6F6A[CE]; _gcl_au=1.1.1220505547.1592978511; PAGENAME=US%2Feprocess-automation; _uetvid=9c077378-00f9-4b15-9f24-c35b88bedd04; ei_client_id=5ef2ecc58f37fb00102d6f0b; OptanonConsent=isIABGlobal=false&datestamp=Wed+Jun+24+2020+14%3A03%3A49+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=5.11.0&landingPath=NotLandingPage&groups=1%3A1%2C0_209922%3A1%2C0_219528%3A1%2C0_219529%3A1%2C2%3A1%2C0_209924%3A1%2C0_209927%3A1%2C0_219567%3A1%2C3%3A1%2C0_209929%3A1%2C4%3A1%2C0_209930%3A1%2C0_209932%3A1%2C0_219467%3A1%2C0_219469%3A1%2C0_219572%3A1%2C0_219752%3A1%2C0_219753%3A1%2C0_219754%3A1%2C0_219903%3A1%2C0_220004%3A1%2C0_220006%3A1%2C0_219568%3A1%2C0_219527%3A1%2C0_219571%3A1%2C0_219573%3A1%2C0_269102%3A1%2C0_269104%3A1%2C0_219530%3A1%2C0_220005%3A1%2C0_219569%3A1%2C0_222456%3A1%2C0_269101%3A1%2C0_269103%3A1%2C0_269105%3A1&AwaitingReconsent=false; incap_ses_1225_2012038=dbfcN3+cBg2EZwTOoBMAER9k9V4AAAAAq+WyliDq+W/I+jxDObHoog==; JSESSIONID_191705=0D9A82CB78E17479412D869D76D0D74D; dtSa=-; dtPC=1$140310635_659h1vLWHGVUCFPQVBCUGNJFFUFLMLOPKHQCBF-0; dtLatC=1; dtCookie=v_4_srv_1_sn_24AB96C33CD259E0778DC8D589678366_perc_100000_ol_0_mul_1_app-3A73600caa6ab1ac15_1; rxvt=1593142146827|1593139550513'
header = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
'Connection': 'keep-alive',
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Cookie': cookie,
'referer': 'https://blog.csdn.net/weixin_37719937'
}
url = 'https://elekta.mastercontrol.com/elekta/index.cfm?infocard_id=4GYURLD6WVBCHLSTLV#/' # csdn 个人中心中，加载名字的js地址
seesion = requests.session()
response = seesion.get(url,headers=header)
#response.coding="gbk"
wbdata = response.text
print("正在打开请求")
print(response.url)
print()
soup = BeautifulSoup(wbdata,'lxml')
print(soup)
