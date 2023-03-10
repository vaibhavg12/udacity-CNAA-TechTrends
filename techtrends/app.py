import logging
import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

#keep count of all access made to db
db_calls_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_calls_count
    db_calls_count +=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get connections count from number of posts
def retrieve_metrics(metrics_object):
    """
    Count the number of news articles and increment the number of connections used for them
    Parameters:
    metrics_object (dict): Dictionary with basic data for metrics endpoint response
    """
    connection = get_db_connection()
    article_count = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()

    metrics_object['db_connection_count'] = db_calls_count
    metrics_object['posts_count'] = article_count[0]    

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.error('Article {} does not exists!'.format(post_id))  
      return render_template('404.html'), 404
    else:
      logging.info('Article "{}" retrieved!'.format(post['title']))  
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('"About Us" page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            logging.info('Article "{}" created'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Define health check functionality
@app.route('/healthz', methods=['GET'])
def healthz():
    response = app.response_class(
        response=json.dumps({'result': 'OK - healthy'}),
        status=200,
        mimetype='application/json')

    return response

# Define metrics functionality
@app.route('/metrics', methods=['GET'])
def metrics():
    metrics_object = {
        'db_connection_count': 0,
        'posts_count': None
    }

    retrieve_metrics(metrics_object)

    response = app.response_class(
        response=json.dumps(metrics_object),
        status=200,
        mimetype='application/json')

    return response

# start the application on port 3111
if __name__ == "__main__":
   stdout_handler = logging.StreamHandler(sys.stdout)
   sdterr_handler = logging.StreamHandler(sys.stderr)
   logging.basicConfig(handlers = [stdout_handler, sdterr_handler],level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
   