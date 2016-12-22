#coding: utf-8
from scrapy.cmdline import execute
import os

if __name__ == '__main__':
    project_name = "Wechatproject"
    spider_name = "wechat"
    results_name = "results/results.json"

    if not os.path.exists(project_name):
        print "Please Edit the project files and Run again!!!"
        s = "scrapy startproject %s" % project_name
        execute(s.split())
    else:
        print "Start Crawling!!!"
        path = os.getcwd() # 获取当前路径
        os.chdir(path+"/"+project_name) # 修改当前路径
        if os.path.exists(results_name):
            os.remove(results_name)
        s = "scrapy crawl %s" % spider_name
        # s = "scrapy crawl %s -o %s -t json" % (spider_name, results_name)
        execute(s.split())
