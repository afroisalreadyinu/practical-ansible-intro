import os
from datetime import datetime
from functools import wraps

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
    __tablename__ = 'user'
    email = db.Column(db.String(), primary_key=True)
    pw_hash = db.Column(db.String(), nullable=False)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=True)
    added = db.Column(db.DateTime(), default=datetime.now)
    user_email = db.Column(db.String, db.ForeignKey('user.email'))

    def to_dict(self):
        return {"text": self.text,
                "added": self.added.strftime("%m.%d.%Y %H:%M")}


def logged_in(handler):
    @wraps(handler)
    def replacement(*args, **kwargs):
        email = session.get('email')
        if not email:
            abort(401)
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(401)
        return handler(user, *args, **kwargs)
    return replacement


@app.route("/")
def index():
    email = session.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if not user:
            session.pop('email')
            email = None
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
    user = User.query.filter_by(email=data['email']).one()
    if custom_app_context.verify(data['password'], user.pw_hash):
        session['email'] = user.email
        return jsonify({"email":user.email})
    return jsonify({"status":"error"})

@app.route("/logout/", methods=["GET"])
def logout():
    session.pop("email")
    return jsonify({"status": "logged_out"})

@app.route("/posts/")
@logged_in
def list_posts(user):
    posts = Post.query.order_by(Post.added.desc()).all()
    return jsonify({'posts':[p.to_dict() for p in posts]})

@app.route("/post/", methods=["POST"])
@logged_in
def create_post(user):
    data = request.get_json()
    post = Post(text=data['text'], user_email=user.email)
    db.session.add(post)
    db.session.commit()
    return jsonify({"status": "OK"})

def run():
    app.debug = True
    app.run(port=6001)

def create_db():
    with app.app_context():
        db.create_all()
