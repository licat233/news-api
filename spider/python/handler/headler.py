import mysql.connector
from bs4 import BeautifulSoup
from tqdm import tqdm

articleTableName = "article"
imageTableName = "image"
categoryTableName = "category"

def createDatabaseConn():
    # 连接MySQL数据库
    cnx = mysql.connector.connect(
        user='root', password='', host='localhost', database='news')
    return cnx

def queryArticle(offset):
    # 执行查询语句
    query = "SELECT * FROM "+articleTableName+" LIMIT 1 OFFSET %s"
    cnx = createDatabaseConn()
    cursor = cnx.cursor()
    data = (offset,)
    cursor.execute(query, data)
    result = cursor.fetchone()

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()
    return result

def updateHtmlContent(content, id):
    # 执行查询语句
    query = "UPDATE "+articleTableName+" SET html_content=%s WHERE id=%s"
    cnx = createDatabaseConn()
    cursor = cnx.cursor()
    data = (content, id)
    cursor.execute(query, data)
    cnx.commit()
    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

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

count = 16634
i = 0
progress_bar = tqdm(total=count)
while i <= count:
    article = queryArticle(i)
    id = article[0]
    content = article[10]
    soup = BeautifulSoup(content, 'html.parser')
    # 查找所有的 figure
    figuresE = soup.find_all('figure')
    # 查找每个下面的img
    for figureE in figuresE:
        imgE = figureE.find('img')
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
progress_bar.close()
