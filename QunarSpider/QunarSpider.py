#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import datetime
import codecs
import multiprocessing as mp
from os import makedirs
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.proxy import *


site = 'http://flight.qunar.com'
hot_city_list = [u'上海', u'北京', u'广州', u'深圳']
num = len(hot_city_list)


def one_driver_ticket(driver, from_city, to_city):
    # time = datetime.datetime.now()
    date = datetime.date.today()
    tomorrow = date+datetime.timedelta(days=1)
    # date格式转为string格式
    tomorrow_string = tomorrow.strftime('%Y-%m-%d')

    driver.find_element_by_name('fromCity').clear()
    driver.find_element_by_name('fromCity').send_keys(from_city)
    driver.find_element_by_name('toCity').clear()
    driver.find_element_by_name('toCity').send_keys(to_city)
    driver.find_element_by_name('fromDate').clear()
    driver.find_element_by_name('fromDate').send_keys(tomorrow_string)
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    time.sleep(5) # 控制间隔时间，等待浏览器反映

    flag = True
    page_num = 0
    while flag:
        # 保存页面
        # print driver.page_source
        source_code = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
        print type(source_code)
        dstdir = u'./ticket/'
        if not exists(dstdir):
            makedirs(dstdir)
        f = codecs.open(dstdir+from_city+u','+to_city+unicode(tomorrow_string)+u','+unicode(str(page_num+1))+u'.html', 'w+', 'utf8')
        f.write(source_code)
        f.close()

        next_page = None
        try:
            next_page = driver.find_element_by_id('nextXI3')
        except Exception as e:
            print e
            pass
        print "page: %d" % (page_num+1)
        if next_page:
            try:
                next_page.click()
                time.sleep(2) # 控制间隔时间，等待浏览器反映
                page_num += 1
            except Exception as e:
                print 'next_page could not be clicked'
                print e
                flag = False
        else:
            flag = False

def get_proxy_list(file_path):
    proxy_list = []
    try:
        f = open(file_path, 'r')
        all_lines = f.readlines() # readlines()每次按行读取整个文件内容，将读取到的内容放到一个列表中，返回list类型。
        for line in all_lines:
            proxy_list.append(line.replace('\r', '').replace('\n', ''))
        f.close()
    except Exception as e:
        print e
    return proxy_list

def ticket_worker_proxy(city_proxy):
    city = city_proxy.split(',')[0]
    proxy = city_proxy.split(',')[1]
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxy,
        'ftpProxy': proxy,
        'sslProxy': proxy,
        'noProxy': '' # 过滤不需要代理的地址
    })
    driver = webdriver.Firefox(proxy=proxy)
    driver.get(site)
    driver.maximize_window() # 将浏览器最大化显示
    for i in xrange(num):
        if city == hot_city_list[i]:
            continue
        from_city = city
        to_city = hot_city_list[i]
        one_driver_ticket(driver, from_city, to_city)
    driver.close()

def all_ticket_proxy():
    hot_city_proxy_list = []
    proxy_list = get_proxy_list('./proxy/proxy.txt') # ./表示当前目录，../表示上一级目录
    for i in xrange(num):
        hot_city_proxy_list.append(hot_city_list[i]+','+proxy_list[i])
    pool = mp.Pool(processes=1)
    pool.map(ticket_worker_proxy, hot_city_proxy_list) # map(f, [x1, x2, x3, x4]) = [f(x1), f(x2), f(x3), f(x4)]
    pool.close()
    pool.join()

def ticket_worker_no_proxy(city):
    driver = webdriver.Firefox()
    # chromedriver = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    # os.environ['webdriver.chrome.driver'] = chromedriver
    # driver = webdriver.Chrome(chromedriver)
    driver.get(site)
    driver.maximize_window() # 将浏览器最大化显示
    time.sleep(5) # 控制间隔时间，等待浏览器反映
    for i in xrange(num):
        if city == hot_city_list[i]:
            continue
        from_city = city
        to_city = hot_city_list[i]
        one_driver_ticket(driver, from_city, to_city)
    driver.close()

def all_ticket_no_proxy():
    pool = mp.Pool(processes=1)
    pool.map(ticket_worker_no_proxy, hot_city_list) # map(f, [x1, x2, x3, x4]) = [f(x1), f(x2), f(x3), f(x4)]
    pool.close()
    pool.join()


if __name__ == '__main__':
    print "start"
    start = datetime.datetime.now()
    # all_ticket_proxy() # proxy
    all_ticket_no_proxy() # no proxy
    end = datetime.datetime.now()
    print "end"
    print "time: ", end-start
