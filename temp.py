import pymysql


db_conn = pymysql.connections.Connection(
    host = 'blog-db.ci0pe1i0qrdh.ap-southeast-1.rds.amazonaws.com',
    port = 3306,
    user='cam',
    password='cammac1914B',
    db='blog_data'
)


conn = db_conn.cursor()
conn.execute('SELECT * FROM posts WHERE id = %s', 
                (1,))
post = conn.fetchone()
print('will this help',type(post))
conn.close()