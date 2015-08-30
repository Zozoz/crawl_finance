# -*- coding: utf-8 -*-

# Scrapy settings for crawl_finance project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawl_finance'

SPIDER_MODULES = ['crawl_finance.spiders']
NEWSPIDER_MODULE = 'crawl_finance.spiders'

DOWNLOAD_DELAY = 0
COOKIES_ENABLED = False

ITEM_PIPELINES = {
        'crawl_finance.pipelines.MusicSqlitePipeline': 500,
        # 'crawl_finance.pipelines.Write2FilePipeline': 500,
        # 'crawl_finance.pipelines.MysqlPipeline': 600,
        # 'crawl_finance.pipelines.MongodbPipeline': 700,
        }

COMMENTSFILEPATH = 'crawl_finance/comments/'


MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'wangyi'

MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWD = '123456'
MYSQL_DB = 'wangyi'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawl_finance (+http://www.yourdomain.com)'
