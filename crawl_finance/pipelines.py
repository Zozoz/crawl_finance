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
        self.dbpool.runQuery("""create table if not exists `wangyi`.`WangyiDirectory`(
                tid varchar(50) not null,
                primary key(tid),
                cid varchar(50) not null,
                tname varchar(50),
                ename varchar(50),
                alias varchar(50),
                subnum int,
                topicid varchar(50)
                )charset='utf8'""")
        self.dbpool.runQuery("""create table if not exists `wangyi`.`WangyiArticle`(
                docid varchar(50) not null,
                primary key(docid),
                url varchar(200) not null,
                url_3w varchar(200),
                title varchar(200) not null,
                digest varchar(200),
                source varchar(50),
                ptime datetime not null,
                mtime datetime not null,
                comments_url varchar(200),
                comments_number int,
                parent_id varchar(200),
                votecount int,
                replycount int,
                content text
                )charset='utf8'""")
        self.dbpool.runQuery("""create table if not exists `wangyi`.`WangyiComment`(
                id int not null auto_increment,
                primary key(id),
                docid varchar(50) not null,
                username varchar(50) not null,
                location varchar(100),
                datetime varchar(100),
                support char(20),
                oppose char(20),
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
        if item['flag'] == 'article':
            if conn.execute("select 1 from WangyiArticle where docid=%s", (item['docid'],)):
                if 'url' in item:
                    conn.execute(
                            """update WangyiArticle set url=%s, url_3w=%s, title=%s, digest=%s, source=%s, parent_id=%s, ptime=%s, mtime=%s, votecount=%s, replycount=%s)
                            where docid=%s""",
                            (
                                item['url'], item['url_3w'], item['title'], item['digest'], item['source'], item['parent_id'],
                                item['ptime'], item['mtime'], item['votecount'], item['replycount'], item['docid']
                            )
                    )
                else:
                    conn.execute("""
                        update WangyiArticle set content=%s, comments_url=%s, comments_number=%s
                        where docid=%s
                        """,
                        (
                            item['content'], item['comments_url'], item['comments_number'], item['docid']
                        )
                    )
            else:
                if 'url' in item:
                    conn.execute(
                            """insert into WangyiArticle (docid, url, url_3w, title, digest, source, parent_id, ptime, mtime, votecount, replycount)
                            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                item['docid'], item['url'], item['url_3w'], item['title'], item['digest'], item['source'], item['parent_id'],
                                item['ptime'], item['mtime'], item['votecount'], item['replycount']
                            )
                    )

        elif item['flag'] == 'comment':
            conn.execute(
                    """insert into WangyiComment (docid, location, datetime, comment, support, oppose)
                    values (%s, %s, %s, %s, %s, %s)""",
                    (
                        item['docid'], item['location'], item['datetime'],
                        item['comment'], item['support'], item['oppose']
                    )
            )

        else:
            if conn.execute("select 1 from WangyiDirectory where tid=%s", (item['tid'],)):
                conn.execute("""
                    update WangyiDirectory set tid=%s, cid=%s, tname=%s, ename=%s, alias=%s, subnum=%s, topicid=%s
                    where tid=%s
                    """,
                    (
                        item['tid'], item['cid'], item['tname'], item['ename'], item['alias'],
                        item['subnum'], item['topicid'], item['tid']
                    )
                )
            else:
                conn.execute("""
                    insert into WangyiDirectory (tid, cid, tname, ename, alias, subnum, topicid)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item['tid'], item['cid'], item['tname'], item['ename'], item['alias'],
                        item['subnum'], item['topicid'],
                    )
                )

    def _handle_error(self, failure, item, spider):
        log.err(failure)



