# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class WechatprojectItem(Item):
    # define the fields for your item here like:
    # name = Field()
    title = Field()
    link = Field()
    content = Field()
    pass
