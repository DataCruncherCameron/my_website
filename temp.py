import pymysql


db_conn = pymysql.connections.Connection(
    host = 'blog-db.ci0pe1i0qrdh.ap-southeast-1.rds.amazonaws.com',
    port = 3306,
    user='cam',
    password='cammac1914B',
    db='blog_data'
)

headers=('id','created','title','content')

conn = db_conn.cursor()
conn.execute('SELECT * FROM posts')
posts = conn.fetchall()
conn.close()

table_data=list()

for i in list(posts):
    table_data.append(dict(zip(headers,i)))
print(table_data)