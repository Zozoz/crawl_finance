# -*- coding: utf-8 -*-


from scrapy import log
from scrapy.exceptions import DropItem
from pymongo import MongoClient
from twisted.enterprise import adbapi


class Write2FilePipeline(object):

    def __init__(self, path):
        self.path = path

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        path = settings.get('COMMENTSFILEPATH', 'comments')
        return cls(path)

    def process_item(self, item, spider):
        if item['docid']  and item['flag'] == 'comment':
            docid = item['docid']
            content = item['username'] + ' - ' + item['location'] + ' - ' + item['datetime'] + \
                    ' - ' + item['support'] + ' - ' + item['oppose'] + '\n'
            content += (item['comment'] + '\n')
            with open(self.path + docid, 'a') as fp:
                fp.write(content.encode('utf-8'))
        return item


class MongodbPipeline(object):

    def __init__(self, server, port, db_name):
        self.server = server
        self.port = port
        self.db = db_name

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        server = settings.get('MONGODB_SERVER', 'localhost')
        port = settings.get('MONGODB_PORT', 27017)
        db = settings.get('MONGODB_DB', 'wangyi')
        return cls(server, port, db)

    def open_spider(self, spider):
        self.client = MongoClient(self.server, self.port)
        self.db = self.client[self.db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        if item['docid']:
            self.db[item_name].insert(dict(item))
        else:
            DropItem('Mongodb-Item do not have docid.')
        return item


class MysqlPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.dbpool.runQuery("""create table if not exists `wangyi`.`WangyiItem`(
                docid varchar(20) not null,
                primary key(docid),
                title varchar(200) not null,
                source varchar(50),
                datetime datetime not null,
                url varchar(100) not null,
                comments_url varchar(200) not null,
                comments_number int,
                flag char(20),
                parent char(20),
                html text not null
                )charset='utf8'""")
        self.dbpool.runQuery("""create table if not exists `wangyi`.`WangyiCommentsItem`(
                docid varchar(20) not null,
                primary key(docid),
                username varchar(50) not null,
                location varchar(100),
                datetime datetime,
                support int,
                oppose int,
                flag char(20),
                comment text not null
                )charset='utf8'""")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        kw = dict(
            host=settings.get('MYSQL_HOST',' localhost'),
            port=settings.get('MYSQL_PORT', 3306),
            user=settings.get('MYSQL_USER', 'root'),
            db=settings.get('MYSQL_DB', 'wangyi'),
            passwd=settings.get('MYSQL_PASSWD', ''),
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **kw)
        return cls(dbpool)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_execute, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _do_execute(self, conn, item, spider):
        if item['flag'] == 'article' and item['docid']:
            if conn.execute("select 1 from WangyiItem where docid=%s", (item['docid'],)):
                conn.execute("""
                    update WangyiItem set url=%s, title=%s, source=%s, parent=%s, datetime=%s, html=%s, comments_url=%s, comments_number=%s
                    where docid=%s
                    """,
                    (
                        item['url'], item['title'], item['source'], item['parent'], item['datetime'],
                        item['html'], item['comments_url'], item['comments_number'], item['docid']
                    )
                )
            else:
                conn.execute(
                        """insert into WangyiItem (docid, url, flag, title, source, parent, datetime, html, comments_url, comments_number)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            item['docid'], item['url'], item['flag'], item['title'], item['source'], item['parent'],
                            item['datetime'], item['html'], item['comments_url'], item['comments_number']
                        )
                )
        elif item['flag'] == 'comments' and item['docid']:
            pass

    def _handle_error(self, failure, item, spider):
        log.err(failure)



