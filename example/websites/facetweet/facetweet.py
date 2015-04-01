import os
from datetime import datetime

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   make_response,
                   flash,
                   abort,
                   g)

from flask.ext.sqlalchemy import SQLAlchemy


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('facetweet', template_folder=tmpl_dir)
app.config.from_envvar("APP_CONFIG")
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=True)
    added = db.Column(db.DateTime(), default=datetime.now)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/links/")
def links():
    links = Post.query.all()
    resp = dict(posts=[dict(text="blah")])
    return jsonify(resp)

@app.route("/")
def add_link():
    pass

def run():
    app.debug = True
    app.run(port=6001)

def create_db():
    with app.app_context():
        db.create_all()
