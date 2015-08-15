# -*- coding: utf-8 -*-

import scrapy


class WangyiDirectory(scrapy.Item):
    flag = scrapy.Field()
    tid = scrapy.Field()
    cid = scrapy.Field()
    tname = scrapy.Field()
    ename = scrapy.Field()
    alias = scrapy.Field()
    subnum = scrapy.Field()
    topicid = scrapy.Field()


class WangyiArticle(scrapy.Item):
    flag = scrapy.Field()
    url = scrapy.Field()
    url_3w = scrapy.Field()
    docid = scrapy.Field()
    parent_id = scrapy.Field()
    title = scrapy.Field()
    digest = scrapy.Field()
    source = scrapy.Field()
    ptime = scrapy.Field()
    mtime = scrapy.Field()
    content = scrapy.Field()
    comments_url = scrapy.Field()
    comments_number = scrapy.Field()
    votecount = scrapy.Field()
    replycount = scrapy.Field()

class WangyiComment(scrapy.Item):
    flag = scrapy.Field()
    docid = scrapy.Field()
    username = scrapy.Field()
    location = scrapy.Field()
    comment = scrapy.Field()
    datetime = scrapy.Field()
    support = scrapy.Field()
    oppose = scrapy.Field()


