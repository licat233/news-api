import mysql.connector
from bs4 import BeautifulSoup
from tqdm import tqdm
import pymysqlpool
import re
import math
import threading

articleTableName = "article"
imageTableName = "image"
categoryTableName = "category"

# pymysqlpool.logger.setLevel('DEBUG')
config={'host':'localhost', 'user':'root', 'password':'', 'database':'news', 'autocommit':True}

# 创建连接池
pool = pymysqlpool.ConnectionPool(size=20, maxsize=20, pre_create_num=20, name='pool', **config)

def listQuery(table_name, page_size, page):
    offset = (page - 1) * page_size
    # 从连接池获取连接
    with pool.get_connection() as cnx:
        # 执行查询语句
        query = "SELECT * FROM " + table_name + " LIMIT %s OFFSET %s"
        cursor = cnx.cursor()
        data = (page_size, offset)
        cursor.execute(query, data)
        result = cursor.fetchall()
        return result

def getTotalCount(table_name):
    total_records = 0
    with pool.get_connection() as cnx:
        # 执行查询语句
        query = "SELECT COUNT(*) FROM " + table_name
        cursor = cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        total_records = result[0]
        return total_records

def queryArticle(offset):
    # 执行查询语句
    query = "SELECT * FROM "+articleTableName+" LIMIT 1 OFFSET %s"
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        data = (offset,)
        cursor.execute(query, data)
        result = cursor.fetchone()
        return result

def updateHtmlContent(content, id):
    # 执行查询语句
    query = "UPDATE "+articleTableName+" SET html_content=%s WHERE id=%s"
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        data = (content, id)
        cursor.execute(query, data)
        cnx.commit()

def move_tag_if_only_child(tag):
    # 判断标签是否是父标签的唯一一个子节点，并且父标签是 div
    if tag.parent.name == 'div' and len(tag.parent.contents) == 1:
        # 移动标签到父标签的 after 位置
        tag.parent.insert_after(tag)
        # 删除空的父标签
        tag.parent.extract()
        move = move_tag_if_only_child(tag)
        return move
    return False

def UpdateContent():
    print("开始处理文章内容")
    total_records = getTotalCount(articleTableName)
    progress_bar = tqdm(total=total_records)
    records_per_page = 20
    total_pages = math.ceil(total_records / records_per_page)
    def handler(article):
        id = article[0]
        content = article[9]
        soup = BeautifulSoup(content, 'html.parser')
        # 查找所有的 figure
        figuresE = soup.find_all('figure')
        # 查找每个下面的img
        for figureE in figuresE:
            imgE = figureE.find('img')
            if imgE is None:
                continue
            img_url = imgE.get('data-src', None)
            if img_url is None:
                img_url = imgE.get('src', None)
                if img_url is None:
                    figureE.extract()
                    continue
            img_tag = soup.new_tag('img')
            img_tag['src'] = img_url
            img_tag['data-src'] = img_url
            figureE.insert_after(img_tag)
            figureE.extract()
        htmlContent = soup.prettify()
        updateHtmlContent(htmlContent, id)
        progress_bar.update(1)
    for page in range(1, total_pages+1):
        articles = listQuery(articleTableName, records_per_page, page)
        tasks = []
        for article in articles:
            t = threading.Thread(target=handler, args=(article,), name=article[0])
            tasks.append(t)
        for t in tasks:
            t.start()
        for t in tasks:
            t.join()
    progress_bar.close()

# UpdateContent();

def updateImageUrl(id, imageURL):
    with pool.get_connection() as cnx:
        query = "UPDATE " + imageTableName + " SET src=%s WHERE id=%s"
        cursor = cnx.cursor()
        data=(imageURL, id)
        cursor.execute(query, data)
        cnx.commit()

def handlerImageURL():
    print("开始处理图片url")
    total_records = getTotalCount(imageTableName)
    progress_bar = tqdm(total=total_records)
    records_per_page = 10
    total_pages = math.ceil(total_records / records_per_page)
    def handler(img):
        id=img[0]
        newUrl = re.sub(r"^http://", "https://", img[2])
        updateImageUrl(id, newUrl)
        progress_bar.update(1)
    for page in range(1, total_pages+1):
        records = listQuery(imageTableName, records_per_page, page)
        tasks=[]
        for record in records:
            t = threading.Thread(target=handler, args=(record,), name=record[0])
            tasks.append(t)
        for t in tasks:
            t.start()
        for t in tasks:
            t.join()
    progress_bar.close()

# handlerImageURL()

def updateArticleImageURL(id, cover, text_content, html_content):
    with pool.get_connection() as cnx:
        query = "UPDATE " + articleTableName + " SET cover=%s, text_content=%s, html_content=%s WHERE id=%s"
        cursor = cnx.cursor()
        data=(cover, text_content, html_content, id)
        cursor.execute(query, data)
        cnx.commit()

def handlerArticleImageURL():
    print("开始处理文章内图片链接")
    total_records = getTotalCount(articleTableName)
    progress_bar = tqdm(total=total_records)
    records_per_page = 20
    total_pages = math.ceil(total_records / records_per_page)
    def handler(article):
        id=article[0]
        cover = re.sub(r"^http://", "https://", article[7])
        text_content = article[8].replace("http://news-storage", "https://news-storage", -1)
        html_content = article[9].replace("http://news-storage", "https://news-storage", -1)
        updateArticleImageURL(id, cover, text_content, html_content)
        progress_bar.update(1)
    for page in range(1, total_pages+1):
        records = listQuery(articleTableName, records_per_page, page)
        tasks=[]
        for record in records:
            t = threading.Thread(target=handler, args=(record,), name=record[0])
            tasks.append(t)
        for t in tasks:
            t.start()
        for t in tasks:
            t.join()
    progress_bar.close()

# handlerArticleImageURL()
