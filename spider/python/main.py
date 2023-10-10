import requests
# import pandas as pd
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
import os
import uuid
import threading
import pymysqlpool
# import sys

# pymysqlpool.logger.setLevel('DEBUG')
config={'host':'localhost', 'user':'root', 'password':'', 'database':'news', 'autocommit':True}

# 创建连接池
pool = pymysqlpool.ConnectionPool(size=25, maxsize=25, pre_create_num=25, name='pool', **config)

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36 Edg/110.0.1587.63',
    #  'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}
proxy = {
    "http": "http://127.0.0.1:7890",  # 代理服务器的IP地址和端口号
    "https": "http://127.0.0.1:7890"  # 代理服务器的IP地址和端口号
}

baseUrl = "https://read01.com/zh-tw"

ossBaseUrl = "https://news-storage.oss-cn-hongkong.aliyuncs.com"

# 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET 。
auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# 填写Bucket名称。
# 注意，这里的endpoint只能使用http，不能使用https，会报错
bucket = oss2.Bucket(auth, 'http://oss-cn-hongkong.aliyuncs.com', 'news-storage')

articleTableName = "article"
imageTableName = "image"
categoryTableName = "category"

def extract_uid(url):
    slash_index = url.rfind("/")  # 查找最后一个斜杠的索引位置
    dot_index = url.rfind(".")  # 查找最后一个点的索引位置
    code = url[slash_index + 1:dot_index]  # 提取斜杠和点之间的部分
    return code

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


def queryCategoryList():
    # 执行查询语句
    query = "SELECT id, uuid, name, raw_name FROM "+categoryTableName
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results


dbCategoriesCache = queryCategoryList()
# 查找栏目id，-1表示不存在

def queryCategoriesID(category_name):
    if category_name == "":
        return -1
    global dbCategoriesCache
    for id, uuid, name, raw_name in dbCategoriesCache:
        if raw_name == category_name:
            return id
    # 如果不存在，则创建
    insert_query = "INSERT INTO "+categoryTableName+" (uuid, name, raw_name) VALUES (%s, %s, %s)"
    uuidV = str(uuid.uuid4())
    data = (uuidV, category_name, category_name)
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        cursor.execute(insert_query, data)
        cnx.commit()
    # 更新
    dbCategoriesCache = queryCategoryList()

    return queryCategoriesID(name)


def queryArticleExist(raw_uid):
    # 执行查询语句
    query = "SELECT COUNT(*) FROM "+articleTableName+" WHERE raw_uid=%s LIMIT 1"
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        data = (raw_uid,)
        cursor.execute(query, data)
        result = cursor.fetchone()
        count = result[0]
        return count != 0

def queryImageExist(source):
    # 执行查询语句
    query = "SELECT * FROM "+imageTableName+" WHERE source =%s LIMIT 1"
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        data = (source,)
        cursor.execute(query, data)
        result = cursor.fetchone()
        if result:
            id = result[0]
            src = result[2]
            if src ==  "":
                query = "DELETE FROM " + imageTableName + " WHERE id=%s"
                cursor.execute(query, (id,))
                cnx.commit()
                return False, ""
            return True, src
        return False, ""

def insertArticle(raw_uid, title, category_name, publish_at, author, cover, text_content, html_content):
    insert_query = "INSERT INTO "+articleTableName + \
        " (uuid, raw_uid, title, category_id, publish_at, author, cover, text_content, html_content, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    uuidV = str(uuid.uuid4())
    tags = category_name
    category_id = queryCategoriesID(category_name)

    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        data = (uuidV, raw_uid, title, category_id, publish_at, author, cover, text_content, html_content, tags)
        cursor.execute(insert_query, data)
        cnx.commit()

def insertImage(source, src):
    # 数据不存在，执行保存或其他操作
    insert_query = "INSERT INTO "+imageTableName+" (source, src) VALUES (%s, %s)"
    data = (source, src)
    with pool.get_connection() as cnx:
        cursor = cnx.cursor()
        cursor.execute(insert_query, data)
        cnx.commit()

def spider_max_page_record(session, category_id):
    params = {
        'page': 9999,
    }
    response = session.get(f'{baseUrl}/{category_id}/',
                           headers=headers, params=params, proxies=proxy)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    activeLiE = soup.find('ul', {"class": "pagination"}).find(
        "li", {"class": "active"})
    pageNumberV = activeLiE.find('a').text
    items = soup.find_all('div', {"class": "list-item"})

    try:
        pageNum = int(pageNumberV)
        record = len(items) + (pageNum-1)*25
        return pageNum, record
    except ValueError:
        print("无法将字符串转换为整数")
    return 0, 0


def spider_page(session, category_id, page):
    params = {
        'page': page,
    }

    response = session.get(f'{baseUrl}/{category_id}/',
                           headers=headers, params=params, proxies=proxy)
    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    title_urls = []
    activeLiE = soup.find('ul', {"class": "pagination"}).find(
        "li", {"class": "active"})
    pageNumber = activeLiE.find('a').text
    if pageNumber != str(page):
        return title_urls, True

    items = soup.find_all('div', {"class": "list-item"})

    for item in items:
        titleE = item.find('div', {"class": "title"})
        title = titleE.text.replace('\xa0', '')
        article_path = titleE.find('a')['href']
        url = baseUrl+article_path
        # 判断文章是否已经存在数据库中
        uid = extract_uid(url)
        exist = queryArticleExist(uid)
        if exist:
            # 若已经存在，则不爬取该文章
            title_urls.append(("", "", "", ""))
            continue
        coverE = item.find('div', {"class": "image"})
        cover = coverE.find('img').get('data-src', "")
        title_urls.append((title, url, cover, uid))

    return title_urls, False


def spider_content(session, url):
    response = session.get(url, headers=headers)
    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    publish_at, meta = soup.find('div', {'class': 'meta'}).text.strip().split('\xa0')
    # 开始识别并移除广告
    # 根据CSS类名进行筛选
    ads = soup.find_all(class_='axslot')
    for ad in ads:
        ad.decompose()  # 直接移除广告标签及其内容
    contentE = soup.find('div', {'class': 'content'})
    # 更换图片url
    imgsE = contentE.find_all('img')
    for imgE in imgsE:
        img_url = imgE.get('data-src', None)
        if img_url is None:
            imgE.decompose()  # 移除
            continue
        if not img_url.startswith('http'):
            # 如果src属性值相对路径，则需要加上文章所在目录的路径
            img_url = os.path.join(os.path.dirname(url), img_url)
        retry_count = 0
        new_img_url = upload_to_oss(img_url, "images")
        while new_img_url == "" and retry_count < 3:
            retry_count += 1
            new_img_url = upload_to_oss(img_url, "images")
        if new_img_url == "":
            return "", "", "", ""
        imgE['src'] = new_img_url
        imgE['data-src'] = new_img_url

    # 处理figure
    # 查找所有的 figure
    figuresE = contentE.find_all('figure')
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

    textContent = contentE.text.strip().replace('\xa0', '')
    htmlContent = contentE.prettify()

    return publish_at, meta, textContent, htmlContent


def generate_random_filename(filename):
    # 获取文件的扩展名
    extension = os.path.splitext(filename)[1]

    # 生成唯一的标识符
    random_string = str(uuid.uuid4().hex)

    # 拼接新的文件名
    new_filename = random_string + extension

    return new_filename


def upload_to_oss(image_url, dirname, count=1):
    # 判断该图片是否已存在于oss中
    exist, src = queryImageExist(image_url)
    if exist and src != "":
        return src

    # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    # 填写网络流地址。
    input = requests.get(image_url)
    # 填写Object完整路径。Object完整路径中不能包含Bucket名称。

    newName = generate_random_filename(image_url)
    global bucket
    try:
        bucket.put_object(f'{dirname}/{newName}', input)
        src = f"{ossBaseUrl}/{dirname}/{newName}"
        insertImage(image_url, src)
        return src
    except oss2.exceptions.ServerError as e:
        # 上传失败，再上传一次，最多允许2次
        count += 1
        if count > 3:
            print(f'上传 {newName} 图片失败，来源：{image_url}')
            return ""
        print(f'再次上传 {newName} 图片，来源：{image_url}')
        return upload_to_oss(image_url, dirname, count)
    return ""

def process_run(tasks):
    n = len(tasks)
    ts_arr1 = tasks[:n//2]
    ts_arr2 = tasks[n//2:]
    for t in ts_arr1:
        t.start()
    for t in ts_arr1:
        t.join()
    for t in ts_arr2:
        t.start()
    for t in ts_arr2:
        t.join()

def category_handler(category_name, category_id):
    retries = 3  # 设置重试次数
    retry_delay = 3  # 设置重试间隔（秒）

    def aticle_handler(session, title, url, cover, raw_uid, callback):
        if title == "" or url == "" or cover == "":
            if callback:
                callback()
            return
        for attempt in range(retries):
            try:
                publish_at, meta, textContent, htmlContent = spider_content(session, url)
                ossCover = upload_to_oss(cover, "covers")
                if ossCover == "":
                    continue
                author = meta.replace('來源：', '')
                insertArticle(raw_uid, title, category_name, publish_at, author, ossCover, textContent, htmlContent)
                break
            except requests.exceptions.RequestException as e:
                print(f'获取 {category_name} 类别的文章失败：{title} (第 {attempt + 1} 次重试)')
                if attempt < retries - 1:
                    print(f'将在 {retry_delay} 秒后重试...')
                    time.sleep(retry_delay)
                else:
                    print(f'达到最大重试次数，放弃获取文章：{title}')
                    break
        if callback:
            callback()

    with requests.Session() as session:
        max_pagenum, max_item = spider_max_page_record(session, category_id)
        # 创建进度条对象
        progress_bar = tqdm(total=max_item)

        def bar_add():
            progress_bar.update(1)
        for page in range(1, max_pagenum+1):
            title_urls, overflow = spider_page(session, category_id, page)
            if overflow:
                break
            # for title, url, cover, uid in title_urls:
            #     aticle_handler(session, title, url, cover, uid, bar_add)
            #     sys.exit(0)
            # 使用多线程
            tasks = []
            for title, url, cover, uid in title_urls:
                if title == "" or url == "" or cover == "":
                    bar_add()
                    continue
                t = threading.Thread(target=aticle_handler, args=(session, title, url, cover, uid, bar_add), name=uid)
                tasks.append(t)
            process_run(tasks)
        progress_bar.close()
    # 写入xlsx文件
    # df = pd.DataFrame(post_infos)
    # df.to_excel(f'{category}.xlsx', index=False)


def main():
    startAt = time.time()

    # count = getTotalCount(articleTableName)
    # print("当前篇数: ", count)
    categories = [('健康', 'c508'), ('美食', 'c710'), ('時尚', 'c942'), ('运势', 'c313'), ('娛樂', 'c475'),
                  ('旅游', 'c808'), ('動漫', 'c921'), ('家居', 'c515'), ('科學', 'c610'), ('文化', 'c502'), ('歷史', 'c616')]
    for category, category_id in categories:
        print(f"开始爬取 【{category}】 类目")
        category_handler(category, category_id)

    endAt = time.time()

    subTime = endAt - startAt

    print("耗时: ", subTime, "秒")


if __name__ == "__main__":
    main()
