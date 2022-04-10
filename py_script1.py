from pymysql import connections
from flask import Flask, render_template, request, url_for, flash, redirect 
from werkzeug.exceptions import abort 


#def get_db_connection():
#    conn = sqlite3.connect('database.db')
#    conn.row_factory = sqlite3.Row
#    return conn 

headers=('id','created','title','content')

db_conn = connections.Connection(
    host = 'blog-db.ci0pe1i0qrdh.ap-southeast-1.rds.amazonaws.com',
    port = 3306,
    user='cam',
    password='cammac1914B',
    db='blog_data'
)


def get_post(post_id):
    conn = db_conn.cursor()
    conn.execute('SELECT * FROM posts WHERE id = %s', 
                        (post_id,))
    post = dict(zip(headers,conn.fetchone()))
    print('will this help',post)
    conn.close()
    if post is None:
        abort(404)
    return post 



app = Flask(__name__)
app.config['SECRET_KEY']='averybigprimenumber'




@app.route('/')
def index():
    conn = db_conn.cursor()
    conn.execute('SELECT * FROM posts')
    posts = conn.fetchall()
    conn.close()
    table_data=list()

    for i in list(posts):
        table_data.append(dict(zip(headers,i)))
    return render_template('index.html', posts=table_data)

    
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET','POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('title is required peasant')
        else:
            conn=db_conn.cursor()
            conn.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
            db_conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')



@app.route('/<int:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post=get_post(post_id)

    if request.method =='POST':
        title=request.form['title']
        content = request.form['content']

        if not title:
            flash('title is required drongo')
        else:
            conn=db_conn.cursor()
            conn.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s',
            (title, content, post_id))
            db_conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = db_conn.cursor()
    conn.execute('DELETE FROM posts WHERE id = %s', (id,))
    db_conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))




if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80, debug=True)

