import mysql.connector
from bs4 import BeautifulSoup
from tqdm import tqdm
from pymysqlpool import ConnectionPool

# 创建连接池
pool = ConnectionPool(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='news',
    pool_name='my_pool',
    pool_size=10  # 连接池大小，根据需要进行调整
)

articleTableName = "article"
imageTableName = "image"
categoryTableName = "category"

def createDatabaseConn():
    # 连接MySQL数据库
    cnx = mysql.connector.connect(
        user='root', password='', host='localhost', database='news')
    return cnx

def queryArticle(offset):
    # 从连接池获取连接
    with pool.get_conn() as cnx:
        # 执行查询语句
        query = "SELECT * FROM " + articleTableName + " LIMIT 1 OFFSET %s"
        cursor = cnx.cursor()
        data = (offset,)
        cursor.execute(query, data)
        result = cursor.fetchone()
    return result

def queryImage(offset):
    # 从连接池获取连接
    with pool.get_conn() as cnx:
        # 执行查询语句
        query = "SELECT * FROM " + imageTableName + " LIMIT 1 OFFSET %s"
        cursor = cnx.cursor()
        data = (offset,)
        cursor.execute(query, data)
        result = cursor.fetchone()

    return result

def handlerImageURL():
    count = 0
    with pool.get_conn() as cnx:
        # 执行查询语句
        query = "SELECT COUNT(*) FROM " + imageTableName
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        count = result[0]
    for i in range(count):
        img = queryImage(i)
        print(img)
        break

handlerImageURL()