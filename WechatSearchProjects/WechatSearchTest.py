#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re
import urllib, urllib2
import requests
import pymongo
import datetime
from bs4 import BeautifulSoup
import multiprocessing as mp


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

# # 保存操作
# def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_contents):
#     posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
#
#     for save_content in save_contents:
#         posts.save(save_content)
# 保存操作
def ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content):
    posts = MongoDBIO(save_host, save_port, save_name, save_password, save_database, save_collection).Connection()
    posts.save(save_content)


def GetTitleUrl(url, data):
    content = requests.get(url=url, params=data).content # GET请求发送
    soup = BeautifulSoup(content)
    tags = soup.findAll("h4")
    titleurl = []
    for tag in tags:
        item = {"title":tag.text.strip(), "link":tag.find("a").get("href"), "content":""}
        titleurl.append(item)
    return titleurl

def GetContent(url):
    soup = BeautifulSoup(requests.get(url=url).content)
    tag = soup.find("div", attrs={"class":"rich_media_content", "id":"js_content"}) # 提取第一个标签
    content_list = [tag_i.text for tag_i in tag.findAll("p")]
    content = "".join(content_list)
    return content

def ContentSave(item):
    # 保存配置
    save_host = "localhost"
    save_port = 27017
    save_name = ""
    save_password = ""
    save_database = "testwechat"
    save_collection = "result"

    save_content = {
        "title":item["title"],
        "link":item["link"],
        "content":item["content"]
    }

    ResultSave(save_host, save_port, save_name, save_password, save_database, save_collection, save_content)

def func(tuple):
    querystring, type, page = tuple[0], tuple[1], tuple[2]
    url = "http://weixin.sogou.com/weixin"
    # get参数
    data = {
        "query":querystring,
        "type":type,
        "page":page
    }

    titleurl = GetTitleUrl(url, data)

    for item in titleurl:
        url = item["link"]
        print "url:", url
        content = GetContent(url)
        item["content"] = content
        ContentSave(item)


if __name__ == '__main__':
    start = datetime.datetime.now()

    querystring = u"清华"
    type = 2 # 2-文章，1-微信号

    # 多进程抓取
    p = mp.Pool()
    p.map_async(func, [(querystring, type, page) for page in range(1, 50, 1)])
    p.close()
    p.join()

    # # 单进程抓取
    # for page in range(1, 50, 1):
    #     tuple = (querystring, type, page)
    #     func(tuple)

    end = datetime.datetime.now()
    print "last time: ", end-start
