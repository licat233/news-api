import mysql.connector

def createDatabaseConn():
    # 连接MySQL数据库
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='news')
    return cnx

def queryCategoryList():
    # 执行查询语句
    query = "SELECT id, name FROM category"
    cnx = createDatabaseConn()
    cursor = cnx.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    # print(results)
    # [(1, '健康'), (2, '動漫'), (3, '娛樂'), (4, '家居'), (5, '文化'), (6, '旅游'), (7, '時尚'), (8, '歷史'), (9, '科學'), (10, '美食'), (11, '运势')]

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()
    return results

# res = queryCategoryList()
# for id, name in res:
#     print(name)

arr = ("a","b","c")
n = len(arr)

arr1 = arr[:n//2]  # 取前半部分元素
arr2 = arr[n//2:]  # 取后半部分元素

print(arr1)  # 打印第一个数组
print(arr2)  # 打印第二个数组
