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
app = Flask('hackerit', template_folder=tmpl_dir)

app.config.from_envvar("APP_CONFIG")

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(), primary_key=True)
    pw_hash = db.Column(db.String(), nullable=False)

class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(), unique=True)
    text = db.Column(db.String())
    user_email = db.Column(db.String(), db.ForeignKey('user.email'))
    points = db.Column(db.Integer)

    def to_dict(self):
        return dict(url=self.url,
                    link_id=self.id,
                    text=self.text)

class Vote(db.Model):
    __tablename__ = 'vote'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_email', 'link_id'),
    )
    user_email = db.Column(db.String(), db.ForeignKey("user.email"))
    link_id = db.Column(db.Integer(), db.ForeignKey("link.id"))
    vote_up = db.Column(db.Boolean(), default=True)


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

@app.route("/link/", methods=["POST"])
@logged_in
def new_link(user):
    data = request.get_json()
    link = Link(url=data['url'],
                text=data['description'],
                user_email=user.email)
    db.session.add(link)
    db.session.commit()
    return jsonify({"status": "OK"})

@app.route("/link/", methods=["GET"])
@logged_in
def list_links(user):
    links = Link.query.all()
    return jsonify({"links": [link.to_dict() for link in links]})

@app.route("/vote/", methods=["POST"])
@logged_in
def vote(user):
    data = request.get_json()
    vote = Vote.query.filter_by(
        link_id=data['link_id'],
        user_email=user.email).first()
    ret_data = None
    if vote:
        if vote.vote_up == data['upvote']:
            #cancellation
            db.session.delete(vote)
            ret_data = {'upvoted': False, 'downvoted': False}
        else:
            vote.vote_up = data['upvote']
            db.session.add(vote)
    else:
        vote = Vote(link_id=data['link_id'],
                    user_email=user.email,
                    vote_up=data['upvote'])
        db.session.add(vote)
    db.session.commit()
    if not ret_data:
        ret_data = {'upvoted':vote.vote_up, 'downvoted': not vote.vote_up}
    return jsonify(ret_data)

def run():
    app.debug = True
    app.run(port=6002)

def create_db():
    with app.app_context():
        db.create_all()
