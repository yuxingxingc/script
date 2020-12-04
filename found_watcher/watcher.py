# -*- coding: utf-8 -*-
import ast
import random
import re
import requests
import time
from lxml import etree
import os

URL = 'http://fundgz.1234567.com.cn/js/'
HEADER = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'}
FUND_LIST = ['519674', '320007', '002621', '160222', '003095', '161005', '161725']
SAD = ['跌了','糟了','不好了','拉胯了']
HAPPY = ['涨了', '起飞了', '牛逼了']
PROXY = {'http': 'http://10.144.1.10:8080'}

# 银河创新成长混合(519674)
# 诺安成长混合(320007)
# 中欧消费主题股票A(002621)
# 国泰国证食品饮料行业指数分级(160222)
# 中欧消费主题股票A(003095)
# 富国天惠(161005)
# 招商中正白酒(161725)

class FoudBug():
    def __init__(self, url, fund):
        self.url = url
        self.fund = fund

    def get_web(self):
        web = self.url + self.fund + '.js' + '?rt=' + self.generate_random()
        try:
            r = requests.get(web, headers=HEADER, proxies=PROXY, timeout=(3,10))
            status = [r.headers, r.status_code]
            r.encoding = 'utf-8'
            html = etree.HTML(r.text, etree.HTMLParser())
        except Exception as E:
            print(E)
            html, status = None, None
        return html, status

    def find_statics(self):
        html, status = self.get_web()
        if html is not None:
            res = etree.tostring(html, encoding='utf-8').decode('utf-8')
            data = re.search(r'({.*})', res)
            return data[0], status
        else:
            return None, None

    def str2dict(self, data):
        fund_info = ast.literal_eval(data)
        return fund_info

    def generate_random(self):
        num = ''
        for i in range(0, 13):
            i = random.randint(0, 9)
            num = num + str(i)
        return num

if __name__ == '__main__':
    try:
        if os.path.exists('found_list.txt'):
            FUND_LIST = []
            with open('found_list.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    FUND_LIST.append(line)
        while True:
            message = []
            data_time = []
            for i in FUND_LIST:
                test = FoudBug(URL, i)
                fund_info, status = test.find_statics()
                if fund_info:
                    fund_info = test.str2dict(fund_info)
                    a = f"{fund_info['name'][0:8]} \t\t " \
                        f"{'↘' if '-' in fund_info['gszzl'] else '↗'} \t {fund_info['gszzl']}%"
                    t = fund_info['gztime']
                else:
                    print(f'{i} 获取失败')
                    a = None
                    t = None
                message.append(a)
                data_time.append(t)
            print(f'数据时间{data_time[0]}')
            # print(message)
            for i in message:
                print(i)
            print('-' * 20)
            time.sleep(30)
    except Exception as e:
        print(e)
        time.sleep(10)
