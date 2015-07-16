#!/usr/bin/env python
# encoding: utf-8


import re
from scrapy.spider import Spider
from scrapy.http import Request

from crawl_finance.items import WangyiItem, WangyiCommentsItem


class WangyiSpider(Spider):
    name = 'wangyi'
    allowed_domains = ['3g.163.com']
    start_urls = [
            'http://3g.163.com/touch/article/list/9ARI6CIDyswang/0-500.html',
            'http://3g.163.com/touch/article/list/9ARI981Lyswang/0-500.html'
            ]
    base_url = 'http://3g.163.com/'

    def __init__(self, date):
        self.date = date
        self.cnt1 = 0
        self.cnt2 = 0

    def parse(self, response):
        url = response.url.split('/')
        if url[3] == 'touch': # json api of article
            body = response.body
            pattern = '\"url\":\"([^\"]+)\"'
            rst = re.findall(pattern, body)
            ptime = re.findall('\"ptime\":\"([^\"]+)\"', body)
            length = len(rst)
            for i in xrange(length):
                if ptime[i].startswith(self.date):
                    item = rst[i]
                    item = item.split('.')
                    item[-2] += '_0'
                    item = '.'.join(item)
                    yield Request(url=item, callback=self.parse)
            """
            # add next API page
            flag = False
            ptime.sort()
            if ptime[-1].split(' ')[0] >= self.date:
                flag = True
            if flag and url[-2] == '9ARI6CIDyswang':
                self.cnt1 += 1
                f = 10 * self.cnt1
                t = 10
                url[-1] = str(f) + '-' + str(t) + '.html'
                url = '/'.join(url)
                yield Request(url=url, callback=self.parse)
            if flag and url[-2] == '9ARI981Lyswang':
                self.cnt2 += 1
                f = 200 * self.cnt2
                t = 200
                url[-1] = str(f) + '-' + str(t) + '.html'
                url = '/'.join(url)
                yield Request(url=url, callback=self.parse)
            """

        elif url[3] == 'money': # article detail
            item = WangyiItem()
            item['flag'] = 'article'
            item['url'] = response.url
            item['docid'] = url[-1].split('_')[0]
            item['title'] = response.xpath('//body/div[contains(@class, "atitle")]/text()').extract()[0]
            tmp = response.xpath('/html/body/div[4]/text()').extract()
            item['datetime'] = tmp[0].strip('\n').strip(' ')
            item['source'] = tmp[1].strip('\n').strip(' ').strip('\t').strip(' ').split(':')[1]
            tmp = response.xpath('/html/body/div[4]/a/text()[1]').extract()[0]
            item['comments_number'] = int(re.search('(\d+)', tmp).group(0))
            item['html'] = response.xpath('/html/body/div[6]').extract()[0].encode('utf-8')
            tmp = response.xpath('/html/body/div[4]/a/@href').extract()[0].split('.')
            tmp[-2] += '_1'
            item['comments_url'] = '.'.join(tmp)
            item['parent'] = '财经'
            yield Request(url=item['comments_url'], callback=self.parse)
            yield item

        elif url[3] == 'money_bbs': # comment detail
            url = response.url
            docid = url.split('/')[-1].split('_')[0]
            print 'docid = ', docid
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

                item = WangyiCommentsItem()
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


