import os
from flask import Flask
from flask.helpers import get_env

from models import db
from views import bp, mail

CASE_BOOLEAN = {
    'true': True,
    'false': False
}


def get_db_local_path():
    return f'/data/db.{get_env()}.db'


def init_config(app):
    """ Load config from environment variables"""
    for (k, v) in os.environ.items():
        value = CASE_BOOLEAN.get(v.lower(), v)
        try:
            value = int(value)
        except ValueError:
            pass
        app.config[k] = value

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'sqlite:///{get_db_local_path()}'
    )


def create(fncs=[
        init_config,
        db.init_app,
        mail.init_app]):

    app = Flask(__name__)

    """ Initialize external module """
    for fnc in fncs:
        fnc(app)

    """ Create database if not exists """
    if not os.path.exists(get_db_local_path()):
        with app.app_context():
            db.create_all()

    """ Register blueprint(s) here """
    app.register_blueprint(bp)

    return app
