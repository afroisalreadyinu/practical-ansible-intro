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
                   jsonify,
                   session)

from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('facetweet', template_folder=tmpl_dir)

app.config.from_envvar("APP_CONFIG")

db = SQLAlchemy(app)

class User(db.Model):
    email = db.Column(db.String(), primary_key=True)
    pw_hash = db.Column(db.String(), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=True)
    added = db.Column(db.DateTime(), default=datetime.now)
    user_email = db.Column(db.String, db.ForeignKey('user.email'))



@app.route("/")
def index():
    email = session.get('email')
    return render_template('index.html', email=email)

@app.route("/signup/", methods=["POST"])
def signup():
    data = request.get_json()
    pw_hash = custom_app_context.encrypt(data['password'])
    user = User(email=data['email'],
                pw_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    session['email'] = user.email
    return jsonify({"email":user.email})

@app.route("/login/", methods=["POST"])
def login():
    data = request.get_json()
    pw_hash = custom_app_context.encrypt(data['password'])
    user = User.query.filter_by(email=data['email']).one()
    if user.pw_hash == pw_hash:
        session['email'] = user.email
        return jsonify({"email":user.email})
    return jsonify({"status":"error"})

@app.route("/logout/", methods=["GET"])
def logout():
    session.pop("email")
    return jsonify({"status": "logged_out"})

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
