#!/usr/bin/env python
# encoding: utf-8


import json
import re
from scrapy.spider import Spider
from scrapy.http import Request

from crawl_finance.items import WangyiArticle, WangyiComment, WangyiDirectory


class WangyiSpider(Spider):
    name = 'wangyi'
    allowed_domains = ['3g.163.com','c.m.163.com']
    start_urls = [
            'http://c.m.163.com/nc/topicset/android/subscribe/manage/listspecial.html'
            ]
    base_url = 'http://c.m.163.com/nc/article/list/'

    def __init__(self, date):
        self.date = date
        self.cnt1 = 0
        self.cnt2 = 0

    def parse(self, response):
        url = response.url.split('/')
        if url[4] == 'topicset':
            body = response.body
            body = json.loads(body)['tList']
            for it in body:
                item = WangyiDirectory()
                item['flag'] = 'list'
                item['tid'] = it['tid']
                item['cid'] = it['cid']
                item['tname'] = it['tname']
                item['ename'] = it['ename']
                item['alias'] = it['alias']
                item['subnum'] = it['subnum']
                item['topicid'] = it['topicid']
                yield item
                # 头条， 娱乐，体育，财经
                if it['tid'] in ['T1348647909107', 'T1348648517839', 'T1348649079062', 'T1348648756099']:
                    url = self.base_url + it['tid'] + '/0-300.html'
                    yield Request(url=url, callback=self.parse)

        elif len(url) > 5 and url[5] == 'list': # json api of article
            parent_id = url[6]
            body = response.body
            body = json.loads(body)[parent_id]
            for it in body:
                if 'url' in it:
                    item = WangyiArticle()
                    item['flag'] = 'article'
                    item['url'] = it['url']
                    item['url_3w'] = it['url_3w']
                    item['docid'] = it['docid']
                    item['parent_id'] = parent_id
                    item['title'] = it['title']
                    item['digest'] = it['digest']
                    item['source'] = it['source']
                    item['ptime'] = it['ptime']
                    item['mtime'] = it['lmodify']
                    item['votecount'] = it['votecount']
                    item['replycount'] = it['replyCount']
                    yield item
                    url = it['url'].split('.')
                    url[-2] += '_0'
                    url = '.'.join(url)
                    if item['mtime'].startswith(self.date):
                        yield Request(url=url, callback=self.parse)

        elif url[2].startswith('3g'): # article detail
            item = WangyiArticle()
            item['flag'] = 'article'
            item['docid'] = url[-1].split('_')[0]
            item['content'] = response.xpath('/html/body/div[6]').extract()[0].encode('utf-8')
            try:
                tmp = response.xpath('/html/body/div[4]/a/text()[1]').extract()[0]
                item['comments_number'] = int(re.search('(\d+)', tmp).group(0))
                tmp = response.xpath('/html/body/div[4]/a/@href').extract()[0].split('.')
                tmp[-2] += '_1'
                item['comments_url'] = '.'.join(tmp)
                yield item
                yield Request(url=item['comments_url'], callback=self.parse)
            except:
                item['comments_number'] = 0
                item['comments_url'] = ''
                yield item

        elif url[2].startswith('comment'): # comment detail
            url = response.url
            docid = url.split('/')[-1].split('_')[0]
            if url.split('.')[-2].endswith('_1'):
                end_url = response.xpath('/html/body/div[7]/a[2]/@href').extract()[0]
                end_url = 'http://comment.3g.163.com' + end_url
                url1 = end_url.split('_')
                url1[-1] = url1[-1].split('.')
                end_num = int(url1[-1][0])
                url1[-1][0] = ';'
                url1[-1] = '.'.join(url1[-1])
                url1 = '_'.join(url1).split(';')
                for i in xrange(2, end_num+1):
                    yield Request(url=url1[0]+str(i)+url1[1], callback=self.parse)
            comments = response.xpath('//div[contains(@class, "review marTop6")]')
            for index, comment in enumerate(comments):
                support = comment.xpath('.//div[contains(@class, "function")]/text()').extract()[1]
                username = comment.xpath('.//span[contains(@class, "name")]/text()').extract()[0]
                datetime = comment.xpath('.//span[contains(@class, "time")]/text()').extract()[0]
                comment = comment.xpath('.//p').extract()

                item = WangyiComment()
                item['flag'] = 'comment'
                item['docid'] = docid
                item['location'] = item['username'] = username
                item['datetime'] = datetime
                item['comment'] = ''
                for it in comment:
                    item['comment'] += it
                item['support'] = support
                item['oppose'] = '0'
                yield item


