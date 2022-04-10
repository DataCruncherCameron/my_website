import pymysql


db_conn = pymysql.connections.Connection(
    host = 'blog-db.ci0pe1i0qrdh.ap-southeast-1.rds.amazonaws.com',
    port = 3306,
    user='cam',
    password='cammac1914B',
    db='blog_data'
)

cur = db_conn.cursor()


cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
            ('Second Post', 'Content for the second post')
            )

db_conn.commit()
db_conn.close()