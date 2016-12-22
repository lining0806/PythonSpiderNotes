# Scrapy settings for Wechatproject project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Wechatproject'

SPIDER_MODULES = ['Wechatproject.spiders']
NEWSPIDER_MODULE = 'Wechatproject.spiders'

ITEM_PIPELINES = ['Wechatproject.pipelines.WechatprojectPipeline'] # add settings
#############################################################################################
# '''if you want to download images'''
# ITEM_PIPELINES = {'Wechatproject.pipelines.WechatprojectPipeline':1, 'Wechatproject.pipelines.MyImagesPipeline':2 # add settings
# IMAGES_STORE = './images'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Wechatproject (+http://www.yourdomain.com)'
