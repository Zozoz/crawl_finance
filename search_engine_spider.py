#!/usr/bin/env python
# encoding: utf-8


import random
import re
# import time
# from urllib import unquote
import requests
import requesocks
from lxml import etree


# http://comment.news.163.com/cache/newlist/news3_bbs(boardId)/ATAO3VRU00014AED_11.html


user_agent = [
    # Safari
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
    'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    # Chrome
    'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'Mozilla/5.0 (Linux; Android 4.1.2; Nexus 7 Build/JZ054K) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) CriOS/27.0.1453.10 Mobile/10B350 Safari/8536.25'
]

cookie = 'GoogleAccountsLocale_session=zh-CN; GMAIL_RTT=607; HSID=AMehahmynucc-GYKk; SSID=AzP2M22PPTypHpn2d; APISID=K8otXKVzPO3-a_15/A3m4r6M5lEjbFv5YZ; SAPISID=DUyRjWpDeY_eYn23/A0opQpPNvE-WAKhvN; SID=DQAAACYBAACpmmt-L3dd9Eau8aJtmFWFAcR9IW4rtCLCvfjSjbBIFXTNxoG4-JpDODWxI5t2pDh7sIaWeEo__ao1fNB1GPentnlLd_IdHdy5wUDGL0uurZ1QgWQudvd2mCXmKqs7zKZ7xshyfbxt18qSaxW7PqeawgdVv3lQxrA1xQo29o28pFZkIJdFnvDkbYcmZ3z_ZbGbZBCHS8JRh50-1Ci5-1MFk84pT0Wsm6gbFThbj4sEqkJ9Ckxev48TyCVssnYKqbQ9WuwOhntGbQ7RdiOUAftrABbURVicPw-6updKZ8VFHlfVfPnbIKbhYLIKn10nrS_TWpS5dB---lMx3rEO-T_ttd8o9iTPHHE1lWjbQmiC7heN1MtQ65VNCWAJ2SDtesNhyiLpVpSLgQHT3dz8sz4w; GOOGLE_ABUSE_EXEMPTION=ID=3f8caebbd3e842f6:TM=1445337923:C=c:IP=45.116.12.100-:S=APGng0v0YstCYbHIaEEsQPU_gKi-G19UiA; NID=72=xs8lGKvQLq4HO__xpX2kRDniriLNoKxVBDGxnX2CrJd1w2wwcY91pVFd00e62jmHVjynd4IVnB7lqA0iQ2ktBuHZLBFbbL2NwCnm_tPGGFd3X2ohepATqgQCWcXbCYKDY5_uP0ojpaQ8eUWYBXDmskN8vj7O6YRdC2pf0bGgUcQEkGlZyt1Z462i041Kj4yYgY6WrNWB0hiYn7iAK25LMy79GHjfktzmIaaOD4pY9PEuHwzi2nVJqc8RS7yE1oodSluyBh3QzEtWd317b91e; DV=YpIveR50qfkaglUftXjD2ofiVLUJoQI; PREF=ID=1111111111111111:FF=2:LD=zh-CN:NW=1:CR=2:TM=1434955588:LM=1445337937:GM=1:SG=1:V=1:S=B0qwbAWo2jpYTOPb'

def get_from_google():
    base_url = 'https://www.google.com.hk/search?'
    keyword = '南京肇事宝马 site:163.com'
    # time1 = 'tbs=cdr:1,cd_min:2015/06/20,cd_max:2015/06/21'
    offset = 0
    url = base_url + 'q=' + keyword  + '&start=' + str(offset) + '&' + 'tbs=lr:lang_1zh-CN,qdr:y' + '&' + 'lr=lang_zh-CN'
    print url
    session = requesocks.session()
    session.proxies = {
            'http': 'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080'
    }
    session.headers = {
            'user-agent': user_agent[random.randint(0, 9)],
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cookie': cookie
    }
    url = 'https://www.google.com/search?q=南京肇事宝马 site:163.com&lr=lang_zh-CN&tbs=lr:lang_1zh-CN,cdr:1,cd_min:2015/6/20,cd_max:2015/6/30'
    r = session.get(url)# , allow_redirects=False)
    print r.url
    fp = open('url.data', 'w')
    print r.status_code
    while r.status_code == 200:
        print offset, ' success...'
        html = etree.HTML(r.content)
        link = html.xpath('//h3[@class="r"]/a/@href')
        for item in link:
            fp.write(item + '\n')
        if len(link) == 10:
            offset += 10
            url = 'https://www.google.com/search?q=南京肇事宝马 site:163.com&lr=lang_zh-CN&tbs=lr:lang_1zh-CN,cdr:1,cd_min:2015/6/20,cd_max:2015/6/30' + '&start=' + str(offset)
            # url = base_url + 'q=' + keyword  + '&start=' + str(offset) + '&' + 'tbs=lr:lang_1zh-CN,qdr:y' + '&' + 'lr=lang_zh-CN'
            # delay = random.randint(5, 15)
            # time.sleep(delay)
            r = session.get(url)
            print r.status_code
        else:
            break
    fp.close()


def get_from_baidu():
    base_url = 'http://www.baidu.com'
    url_0 = 'http://www.baidu.com/s?tn=sitesowang&tr=mbxnW11j9Df&word='
    word = '南京肇事宝马 site:163.com'
    url = url_0 + word
    r = requests.get(url)
    if r.status_code == 200:
        cnt = 0
        html = etree.HTML(r.text)
        next_page = html.xpath('//div[contains(@id, "page")]/a/@href')
        content = html.xpath('//div[contains(@id, "content_left")]/div/h3/a/@href')
        fp = open('url.data', 'w')
        for item in content:
            fp.write(item + '\n')
        for url in next_page:
            print 'cnt = ', cnt
            cnt += 1
            r = requests.get(base_url + url)
            html = etree.HTML(r.text)
            content = html.xpath('//div[contains(@id, "content_left")]/div/h3/a/@href')
            for item in content:
                fp.write(item + '\n')
        fp.close()


def get_article(url_file, article_file):
    article = 0
    final = open(article_file, 'w')
    with open(url_file, 'r') as fp:
        for url in fp:
            try:
                r = requests.get(url.strip('\n'), timeout=5)

                # get article information
                html = etree.HTML(r.text)
                title = html.xpath('//h1[contains(@id, "h1title")]/text()')[0].encode('gb2312')
                ptime = '20' + '-'.join(r.url.split('/')[-4:-2]) + ' ' + r.url.split('/')[-2]
                source = html.xpath('//div[contains(@class, "ep-time-soure")]/a/text()')[0].encode('gb2312')
                content = html.xpath('//div[contains(@id, "endText")]')[0]
                content = etree.tostring(content)
                docid = r.url.split('/')[-1].split('.')[0]

                # get comment information
                # replyCount = re.compile("replyCount = ([\d]+),").search(r.text).group(1)
                totalCount = re.compile("totalCount = ([\d]+),").search(r.text).group(1)
                threadId = re.compile("threadId = \"([\w]+)\",").search(r.text).group(1)
                boardId = re.compile("boardId = \"([\w]+)\",").search(r.text).group(1)
                tieChannel = re.compile("tieChannel = \"([\w]+)\"").search(r.text).group(1)
                # print replyCount, ' ', totalCount, " ", threadId, " ", boardId, " ", tieChannel
                comment_url = 'http://comment.' + tieChannel + '.163.com/' + boardId + '/' + threadId + '.html'

                # write to file
                final.write(ptime + '\t')
                final.write(docid + '\t')
                final.write(title + '\t')
                final.write(source + '\t')
                # final.write(content + '\t')
                final.write(totalCount + '\t')
                final.write(comment_url + '\t')
                final.write(r.url + '\n')

                article += 1
                print 'article = ', article
            except:
                continue
    final.close()


def sort_file(filename):
    fp = open(filename, 'r')
    tmp = []
    for line in fp:
        tmp.append(line)
    tmp.sort()
    fp.close()
    fp = open(filename, 'w')
    last_item = ''
    for item in tmp:
        if item.split('\t')[1] != last_item:
            fp.write(item)
        last_item = item.split('\t')[1]
    fp.close()


if __name__ == '__main__':
    # get_article('wangyi_all', 'baoma.data')
    # sort_file('baoma.data')
    get_from_google()


