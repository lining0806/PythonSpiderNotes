#coding: utf-8
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from Wechatproject.items import WechatprojectItem
from bs4 import BeautifulSoup
from scrapy.http import Request


class WechatSpider(BaseSpider):
    #############################################################################################
    '''微信搜索程序'''
    name = "wechat"

    start_urls = []
    querystring = u"清华"
    type = 2 # 2-文章，1-微信号
    for i in range(1, 50, 1):
        start_urls.append("http://weixin.sogou.com/weixin?type=%d&query=%s&page=%d" % (type, querystring, i))
    # print start_urls

    #############################################################################################
    ## 递归抓取

    ## 使用xpath()方法，注意item中键对值为string类型，extract()方法返回list
    def parse(self, response):
        # print response.body
        sel = Selector(response)
        sites = sel.xpath('//div[@class="txt-box"]/h4/a')
        for site in sites:
            item = WechatprojectItem()
            item["title"] = site.xpath("text()").extract() # 其中在item.py中定义了title = Field()
            item["link"] = site.xpath("@href").extract() # 其中在item.py中定义了link = Field()
            #############################################################################################
            # yield item ## 只抓取当前页数据
            next_url = item["link"][0]
            # yield Request(url=next_url, callback=self.parse2) ## 只抓取二级页面数据
            yield Request(url=next_url, meta={"item":item}, callback=self.parse2) ## 抓取当前页数和二级页面数据

    ## 使用BeautifulSoup方法，注意item中键对值为string类型
    def parse(self, response):
        # print response.body
        soup = BeautifulSoup(response.body)
        tags = soup.findAll("h4")
        for tag in tags:
            item = WechatprojectItem()
            item["title"] = tag.text # 其中在item.py中定义了title = Field()
            item["link"] = tag.find("a").get("href") # 其中在item.py中定义了link = Field()
            #############################################################################################
            # yield item ## 只抓取当前页数据
            next_url = item["link"]
            # yield Request(url=next_url, callback=self.parse2) ## 只抓取二级页面数据
            yield Request(url=next_url, meta={"item":item}, callback=self.parse2) ## 抓取当前页数和二级页面数据

    def parse2(self, response):
        soup = BeautifulSoup(response.body)
        tag = soup.find("div", attrs={"class":"rich_media_content", "id":"js_content"}) # 提取第一个标签
        content_list = [tag_i.text for tag_i in tag.findAll("p")]
        content = "".join(content_list)
        # print content
        # item = WechatprojectItem() ## 只抓取二级页面数据
        item = response.meta['item'] ## 抓取当前页数和二级页面数据
        item["content"] = content
        return item
