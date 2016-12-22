#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re
import urllib, urllib2
import requests
import pymongo
import datetime
import multiprocessing as mp


Category_Map = {
    "1":u"外汇",
    "2":u"股市",
    "3":u"商品",
    "4":u"债市",
    "5":u"央行",
    "9":u"中国",
    "10":u"美国",
    "11":u"欧元区",
    "12":u"日本",
    "13":u"英国",
    "14":u"澳洲",
    "15":u"加拿大",
    "16":u"瑞士",
    "17":u"其他地区"
}
def num2name(category_num):
    if Category_Map.has_key(category_num):
        return Category_Map[category_num]
    else:
        return ""

class MongoDBIO:
    # 申明相关的属性
    def __init__(self, host, port, name, password, database, collection):
        self.host = host
        self.port = port
        self.name = name
        self.password = password
        self.database = database
        self.collection = collection

    # 连接数据库，db和posts为数据库和集合的游标
    def Connection(self):
        # connection = pymongo.Connection() # 连接本地数据库
        connection = pymongo.Connection(host=self.host, port=self.port)
        # db = connection.datas
        db = connection[self.database]
        if self.name or self.password:
            db.authenticate(name=self.name, password=self.password) # 验证用户名密码
        # print "Database:", db.name
        # posts = db.cn_live_news
        posts = db[self.collection]
        # print "Collection:", posts.name
        return posts

# 保存操作
# def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_contents):
#     posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
#     for save_content in save_contents:
#         posts.save(save_content)
def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content):
    posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
    posts.save(save_content)

def Spider(url, data):
    # # 方法1：requests get
    content = requests.get(url=url, params=data).content # GET请求发送
    # # 方法2：urllib2 get
    # data = urllib.urlencode(data) # 编码工作，由dict转为string
    # full_url = url+'?'+data
    # print full_url
    # content = urllib2.urlopen(full_url).read() # GET请求发送
    # # content = requests.get(full_url).content # GET请求发送
    # print type(content) # str
    return content

def ContentSave(item):
    # 保存配置
    save_host = "localhost"
    save_port = 27017
    save_name = ""
    save_password = ""
    save_database = "textclassify"
    save_collection = "WallstreetcnSave"

    source = "wallstreetcn"
    createdtime = datetime.datetime.now()
    type = item[0]
    content = item[1].decode("unicode_escape") # json格式数据中，需从'\\uxxxx'形式的unicode_escape编码转换成u'\uxxxx'的unicode编码
    content = content.encode("utf-8")
    # print content
    # district的筛选
    categorySet = item[2]
    category_num = categorySet.split(",")
    category_name = map(num2name, category_num)
    districtset = set(category_name)&{u"中国", u"美国", u"欧元区", u"日本", u"英国", u"澳洲", u"加拿大", u"瑞士", u"其他地区"}
    district = ",".join(districtset)
    propertyset = set(category_name)&{u"外汇", u"股市", u"商品", u"债市"}
    property = ",".join(propertyset)
    centralbankset = set(category_name)&{u"央行"}
    centralbank = ",".join(centralbankset)
    save_content = {
        "source":source,
        "createdtime":createdtime,
        "content":content,
        "type":type,
        "district":district,
        "property":property,
        "centralbank":centralbank
    }
    ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content)

def func(page):
    url = "http://api.wallstreetcn.com/v2/livenews"
    # get参数
    data = {
        "page":page
    }
    content = Spider(url, data)
    items = re.findall(r'"type":"(.*?)","codeType".*?"contentHtml":"(.*?)","data".*?"categorySet":"(.*?)","hasMore"', content) # 正则匹配
    if len(items) == 0:
        print "The End Page:", page
        data = urllib.urlencode(data) # 编码工作，由dict转为string
        full_url = url+'?'+data
        print full_url
        sys.exit(0) # 无错误退出
    else:
        print "The Page:", page, "Downloading..."
        for item in items:
            ContentSave(item)


if __name__ == '__main__':

    start = datetime.datetime.now()

    start_page = 1
    end_page = 3300


    # 多进程抓取
    pages = [i for i in range(start_page, end_page)]
    p = mp.Pool()
    p.map_async(func, pages)
    p.close()
    p.join()


    # 单进程抓取
    page = end_page

    while 1:
        url = "http://api.wallstreetcn.com/v2/livenews"
        # get参数
        data = {
            "page":page
        }
        content = Spider(url, data)
        items = re.findall(r'"type":"(.*?)","codeType".*?"contentHtml":"(.*?)","data".*?"categorySet":"(.*?)","hasMore"', content) # 正则匹配
        if len(items) == 0:
            print "The End Page:", page
            data = urllib.urlencode(data) # 编码工作，由dict转为string
            full_url = url+'?'+data
            print full_url
            break
        else:
            print "The Page:", page, "Downloading..."
            for item in items:
                ContentSave(item)
            page += 1

    end = datetime.datetime.now()
    print "last time: ", end-start
