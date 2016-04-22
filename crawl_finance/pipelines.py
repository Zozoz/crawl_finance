# -*- coding: utf-8 -*-


import sqlite3
import MySQLdb
from scrapy import log
from scrapy.exceptions import DropItem
from pymongo import MongoClient
from twisted.enterprise import adbapi


class MusicMysqlPipeline(object):

    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur
        self.cur.execute("""
                create table if not exists music_wangyimusic(
                sm_id varchar(50) primary key,
                user_name varchar(50),
                user_id varchar(50),
                cat varchar(50),
                title varchar(50),
                ctime varchar(50),
                tags varchar(100),
                pnum int,
                colnum int,
                shnum int,
                comnum int
                );"""
        )

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        db = settings.get('SQLITE_DB', 'wangyi_music.db')
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        host = settings.get('MYSQL_HOST', 'localhost')
        port = settings.get('MYSQL_PORT', 3306)
        user = settings.get('MYSQL_USER', 'root')
        passwd = settings.get('MYSQL_PASSWD', 'qwert123456')
        db = settings.get('MYSQL_DB', 'wangyi')
        conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        cur = conn.cursor()
        return cls(conn, cur)

    def process_item(self, item, spider):
        sql0 = 'select 1 from music_wangyimusic where sm_id=%s'
        sql1 = 'update music_wangyimusic set user_name=%s, user_id=%s, cat=%s, title=%s, ctime=%s, tags=%s, pnum=%s, colnum=%s, shnum=%s, comnum=%s where sm_id=%s'
        sql2 = 'insert into music_wangyimusic (sm_id, user_name, user_id, cat, title, ctime, tags, pnum, colnum, shnum, comnum) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        params1 = (item['user_name'],  item['user_id'], item['cat'], item['title'], item['ctime'], item['tags'], item['pnum'], item['colnum'], item['shnum'], item['comnum'], item['sm_id'])
        params2 = (item['sm_id'], item['user_name'],  item['user_id'], item['cat'], item['title'], item['ctime'], item['tags'], item['pnum'], item['colnum'], item['shnum'], item['comnum'])

        self.cur.execute(sql0, (item['sm_id'], ))
        if not self.cur.fetchone():
            self.cur.execute(sql2, params2)
        else:
            self.cur.execute(sql1, params1)
        self.conn.commit()
        return item

        # sql = 'select 1 from wangyimusic where sm_id=?'
        # self.cur.execute(sql, (item['sm_id'],))
        # if not self.cur.fetchone():
        #     self.cur.execute("""insert into wangyimusic (sm_id, user_name, user_id, cat, title,
        #             ctime, tags, pnum, colnum, shnum, comnum)
        #             values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        #         (
        #             item['sm_id'], item['user_name'], item['user_id'], item['cat'], item['title'],
        #             item['ctime'], item['tags'], item['pnum'], item['colnum'], item['shnum'], item['comnum']
        #         )
        #     )
        #     self.conn.commit()
        # return item


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


class TencentMysqlPipeline(object):
    """
    twisted.enterprise.adbapi: Twisted RDBMS support.
    https://twistedmatrix.com/documents/14.0.0/core/howto/rdbms.html
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.dbpool.runQuery("""create table if not exists `wangyi`.`TencentArticle`(
                docid varchar(50) not null,
                primary key(docid),
                url varchar(200),
                title varchar(200),
                digest varchar(200),
                source varchar(50),
                time datetime,
                comments_url varchar(200),
                comments_id varchar(50),
                comments_number int,
                parent_name varchar(200),
                content text
                )charset='utf8'""")
        self.dbpool.runQuery("""create table if not exists `wangyi`.`TencentComment`(
                id int not null auto_increment,
                primary key(id),
                docid varchar(50) not null,
                comments_id varchar(50),
                sex char(10),
                username varchar(50),
                reply_id varchar(50),
                agree_count int,
                datetime varchar(100),
                comment text
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
        """
        conn.runQuery() <--> cursor.execute(), return cursor.fetchall();
        conn.execute(), then result = conn.fetchall()
        """
        if item['flag'] == 'article':
            if conn.execute("select 1 from TencentArticle where docid=%s", (item['docid'],)):
                if not item['content']:
                    try:
                        conn.execute(
                            """update TencentArticle set url=%s, title=%s, digest=%s, source=%s, parent_name=%s, time=%s,
                            comments_id=%s, comments_url=%s  where docid=%s""",
                            (
                                item['url'], item['title'], item['digest'], item['source'], item['parent_name'],
                                item['time'], item['comments_id'], item['comments_url'], item['docid']
                            )
                        )
                    except:
                        conn.execute(
                            """update TencentArticle set comments_number=%s where docid=%s""",
                            (item['comments_number'], item['docid'])
                        )
                else:
                    conn.execute(
                        """update TencentArticle set content=%s where docid=%s""",
                        (item['content'], item['docid'])
                    )
            else:
                conn.execute(
                        """insert into TencentArticle (docid, comments_number)
                        values (%s, %s)""",
                        (
                            item['docid'], item['comments_number']
                        )
                )

        elif item['flag'] == 'comment':
            try:
                conn.execute(
                        """insert into TencentComment (docid, comments_id, datetime, comment, username, sex,
                        reply_id, agree_count) values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            item['docid'], item['comments_id'], item['datetime'], item['comment'],
                            item['username'], item['sex'], item['reply_id'], item['agree_count']
                        )
                )
            except:
                conn.execute(
                        """update TencentComment set agree_count=%s where reply_id=%s""",
                        (item['agree_count'], item['reply_id'])
                )

    def _handle_error(self, failure, item, spider):
        log.err(failure)


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
            if conn.execute("select 1 from wangyi_WangyiArticle where docid=%s", (item['docid'],)):
                if 'url' in item:
                    conn.execute(
                            """update wangyi_WangyiArticle set url=%s, url_3w=%s, title=%s, digest=%s, source=%s, parent_id=%s, ptime=%s, mtime=%s, votecount=%s, replycount=%s
                            where docid=%s""",
                            (
                                item['url'], item['url_3w'], item['title'], item['digest'], item['source'], item['parent_id'],
                                item['ptime'], item['mtime'], item['votecount'], item['replycount'], item['docid']
                            )
                    )
                else:
                    conn.execute("""
                        update wangyi_WangyiArticle set content=%s, comments_url=%s, comments_number=%s
                        where docid=%s
                        """,
                        (
                            item['content'], item['comments_url'], item['comments_number'], item['docid']
                        )
                    )
            else:
                if 'url' in item:
                    conn.execute(
                            """insert into wangyi_WangyiArticle (docid, url, url_3w, title, digest, source, parent_id, ptime, mtime, votecount, replycount)
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


