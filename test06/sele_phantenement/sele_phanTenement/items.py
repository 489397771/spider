# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SelePhantenementItem(scrapy.Item):
    title = scrapy.Field()
    detail = scrapy.Field()
    address = scrapy.Field()
    money = scrapy.Field()
    sendTime = scrapy.Field()
    name = scrapy.Field()