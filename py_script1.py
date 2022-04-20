from pymysql import connections
from flask import Flask, render_template, request, url_for, flash, redirect 
from werkzeug.exceptions import abort

# Packages for call to secrets manager. 
import boto3
import base64
from botocore.exceptions import ClientError

# Make call to secrets manager 
def get_secret():

    secret_name = "blog_website/mysql"
    region_name = "ap-southeast-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    secret=secret[1:-2]
    secret=secret.replace('"','')
    secret_chunk_array=secret.split(',')

    keys=[]
    values=[]

    for i in range(0,len(secret_chunk_array)):
            key_value=secret_chunk_array[i].split(':')
            keys.append(key_value[0])
            values.append(key_value[1])

    secret_dict=dict(zip(keys,values))
    return(secret_dict)

secret=get_secret()
            










headers=('id','created','title','content')

db_conn = connections.Connection(
    host = secret['host'],
    port = secret['port'],
    user= secret['user'],
    password= secret['password'],
    db= secret['dbInstanceIdentifier']
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

