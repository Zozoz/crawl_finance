# -*- coding: utf-8 -*-


from urllib import unquote
from scrapy.spider import Spider
from scrapy.http import Request

from crawl_finance.items import WangyiMusic


class MusicSpider(Spider):
    name = "music"
    allowed_domains = ["music.163.com"]
    start_urls = (
            'http://music.163.com/discover/playlist',
    )
    base_url = 'http://music.163.com'

    def parse(self, response):
        url = response.url.split('/')
        if url[-1].startswith('?cat'):
            urls = response.xpath("//ul/li/p[contains(@class, 'dec')]/a/@href").extract()
            for url in urls:
                url = self.base_url + url
                yield Request(url=url, callback=self.parse)
        elif url[-1].startswith('playlist?id'):
            sm_id = url[-1].split('=')[-1]
            title = response.xpath("//div[contains(@class, 'tit')]/h2/text()").extract()[0]
            user_id = response.xpath("//div[contains(@class, 'user ')]/a[contains(@class, 'face')]/@href").extract()[0].split('=')[-1]
            user_name = response.xpath("//div[contains(@class, 'user ')]/span/a[contains(@class, 's-fc7')]/text()").extract()[0]
            ctime = response.xpath("//div[contains(@class, 'user ')]/span[contains(@class, 'time ')]/text()").extract()[0]
            colnum = response.xpath("//div[contains(@class, 'btns f-cb')]/a[contains(@class, 'u-btni-fav')]/@data-count").extract()[0]
            shnum = response.xpath("//div[contains(@class, 'btns f-cb')]/a[contains(@class, 'u-btni-share')]/@data-count").extract()[0]
            comnum = response.xpath("//div[contains(@class, 'btns f-cb')]/a[contains(@class, 'u-btni-cmmt')]/i/span/text()").extract()[0]
            tags = response.xpath("//div[contains(@class, 'tags f-cb')]/a/i/text()").extract()
            tag = ' '
            for item in tags:
                tag += (item + ';')
            pnum = response.xpath("//div[contains(@class, 'more s-fc3')]/strong/text()").extract()[0]
            item = WangyiMusic()
            item['sm_id'] = sm_id
            cat =  response.request.headers.get('referer', '').split('=')[1].split('&')[0]
            item['cat'] = unquote(cat).decode('utf-8')
            item['title'] = title
            item['user_id'] = user_id
            item['user_name'] = user_name
            item['ctime'] = ctime
            item['colnum'] = colnum
            item['shnum'] = shnum
            item['comnum'] = comnum
            item['tags'] = tag
            item['pnum'] = pnum
            yield item
        else:
            cats = response.xpath("//dd/a[contains(@class, 's-fc1')]/@href").extract()
            names = response.xpath("//dd/a[contains(@class, 's-fc1')]/@data-cat").extract()
            for cat, name in zip(cats, names):
                urls = self.base_url + cat + '&order=hot'
                for i in xrange(50):
                    url = urls + '&limit=35&offset=' + str(35 * i)
                    yield Request(url=url, callback=self.parse)



