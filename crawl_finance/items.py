# -*- coding: utf-8 -*-

import scrapy


class CrawlFinanceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WangyiItem(scrapy.Item):
    flag = scrapy.Field()
    url = scrapy.Field()
    docid = scrapy.Field()
    parent = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    datetime = scrapy.Field()
    html = scrapy.Field()
    comments_url = scrapy.Field()
    comments_number = scrapy.Field()


class WangyiCommentsItem(scrapy.Item):
    flag = scrapy.Field()
    docid = scrapy.Field()
    username = scrapy.Field()
    location = scrapy.Field()
    comment = scrapy.Field()
    datetime = scrapy.Field()
    support = scrapy.Field()
    oppose = scrapy.Field()


