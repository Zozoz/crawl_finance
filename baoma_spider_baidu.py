#!/usr/bin/env python
# encoding: utf-8


import re
import requests
from lxml import etree


# http://comment.news.163.com/cache/newlist/news3_bbs(boardId)/ATAO3VRU00014AED_11.html


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

def get_article():
    article = 0
    final = open('baoma2.data', 'w')
    with open('url.data', 'r') as fp:
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
    # get_article()
    sort_file('baoma2.data')
