import pymysql

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "122121"
MYSQL_PORT = "3306"
MYSQL_DB = "python"

conn = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, charset="utf8")
cur = conn.cursor()


class LinkMysql(object):
    """
    :exception
        ret = linkMysql.select_url(title)
            if ret[0] == 1:
                print("已经存在了")
                pass
            else:
                Sql.insert_content(author, title, intro, category, content)
                print("储存完毕")
    """
    @classmethod
    def insert_data(cls, author, title, intro, category, content):
        """
        数据库写入操作
        对于sql语句而言：
        author，title，intro，category，content，为变量，用的时候要改成对应的列名
        Note：sheetName也是变量，对应的是所建的表名，用的时候也得改成对应表名

        """
        sql = "INSERT INTO sheetName (author, title, intro, category, content)VALUES(%s, %s, %s, %s, %s)"
        try:
            cur.execute(sql, (author, title, intro, category, content))
            conn.commit()
            print('插入成功')
        except Exception as e:
            import traceback
            traceback.print_exc()
            # 发生错误时回滚
            conn.rollback()
        finally:
            # 关闭游标连接
            cur.close()
            # 关闭数据库连接
            conn.close()

    @classmethod
    def select_url(cls, title):
        """
        数据库去重操作
        title:查询上次写入后的结果是否有现在写入的title
        当然title是可变参量，是代表一个列表中的属性，用的时候在对应属性
        fetchall()：返回一个列表，
        """
        sql = "select exists(select 1 from sheelName where title=%s)"
        cur.execute(sql, (title,))
        return cur.fetchall()[0]

