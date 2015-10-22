# -*- coding: utf-8 -*-


import json
from datetime import datetime
from scrapy import Spider, Request

from crawl_finance.items import TencentArticle, TencentComment


class TencentSpider(Spider):
    name = "tencent"
    allowed_domains = ["qq.com"]
    start_urls = (
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_top', # 要闻
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_js', # 江苏
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_mil', # 军事
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_ssh', # 社会
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_ent', # 娱乐
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_sports', # 体育
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_istock', # 股票
            'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=9224f71108b3a1f5&chlid=news_news_finance' # 财经
    )

    def __init__(self, date):
        self.date = date

    def parse(self, response):
        url = response.url.split('/')
        # get article ids
        if url[3].startswith('getQQNewsIndex'):
            body = response.body
            body = json.loads(body)['idlist'][0]['ids']
            chlid = response.url.split('=')[-1]
            ids = []
            cnt = 0
            for it in body:
                cnt += 1
                ids.append(it['id'])
                item = TencentArticle()
                item['flag'] = 'article'
                item['docid'] = it['id']
                item['comments_number'] = it['comments']
                item['content'] = ''
                yield item
                if cnt % 20 == 0:
                    ids = ','.join(ids)
                    url = 'http://r.inews.qq.com/getQQNewsListItems?uid=9224f71108b3a1f5' + '&ids=' + ids + '&chlid=' + chlid
                    yield Request(url=url, callback=self.parse)
                    ids = []

        # get article info
        elif url[3].startswith('getQQNewsList'):
            body = response.body
            print json.loads(body)
            newslist = json.loads(body)['newslist']
            for news in newslist:
                if not news['time'].startswith(self.date):
                    continue
                item = TencentArticle()
                item['flag'] = 'article'
                item['docid'] = news['id']
                item['parent_name'] = news['uinname']
                item['url'] = news['url']
                item['title'] = news['title']
                item['digest'] = news['abstract']
                item['source'] = news['source']
                item['time'] = news['time']
                item['content'] = ''
                item['comments_id'] = news['commentid']
                tmp = news['url'].split('/')
                tmp[3] = 'comment'
                item['comments_url'] = '/'.join(tmp) + '#' + news['commentid']
                item['comments_number'] = 0
                yield item
                url = 'http://view.inews.qq.com/a/' + item['docid']
                yield Request(url=url, callback=self.parse)
                url = 'http://r.inews.qq.com/getQQNewsComment?uid=9224f71108b3a1f5&comment_id=%s&page=%s' % (item['comments_id'], 1)
                yield Request(url=url, callback=self.parse)

        # get comment
        elif url[3].startswith('getQQNewsComment'):
            body = response.body
            comments = json.loads(body)['comments']['new']
            if comments:
                url = response.url.split('=')
                url[-1] = str(int(url[-1]) + 1)
                url = '='.join(url)
                yield Request(url=url, callback=self.parse)
            for comment in comments:
                for it in comment:
                    item = TencentComment()
                    item['flag'] = 'comment'
                    item['docid'] = it['article_id']
                    item['comments_id'] = it['commentid']
                    item['username'] = it['mb_nick_name'] if it['mb_nick_name'] else it['nick']
                    item['comment'] = it['reply_content']
                    item['datetime'] = datetime.fromtimestamp(int(it['pub_time'])).strftime('%Y-%m-%d %H:%M:%S')
                    item['sex'] = it['sex']
                    item['reply_id'] = it['reply_id']
                    item['agree_count'] = it['agree_count']
                    yield item

        # get article content
        else:
            item = TencentArticle()
            item['flag'] = 'article'
            item['docid'] = url[-1]
            try:
                item['content'] = response.xpath('//div[@id="content"]').extract()[0]
            except:
                item['content'] = 'no content'
            yield item


