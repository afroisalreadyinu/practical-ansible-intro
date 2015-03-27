import os
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   make_response,
                   flash,
                   abort,
                   g)


class Config(object):
    SECRET_KEY = "ild#L6Jx/uSfB\x0c]`pQZ 9yKr>8o\r7W)_0?A{'baw"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://USERNAME:PASSWD@localhost/professor'
    UPLOAD_FOLDER = '/var/www/downloads'
    BASE_URL = "http://janslaby.com"
    DOWNLOADS_LOCATION = "downloads"

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('facetweet', template_folder=tmpl_dir)
# config = DevConfig if socket.gethostname() == 'kittie' else ProductionConfig
# app.config.from_object(config)
# db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template('index.html')

def run():
    app.debug = True
    app.run(port=6001)

def db():
    with app.app_context():
        db.create_all()
