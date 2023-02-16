from flask import Flask, request
from flask_babel import Babel
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.momentjs import MomentJS
from config import LANGUAGES

app = Flask(__name__)
app.config.from_object('config')
app.blog_name = 'Custom Blog'

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)

app.jinja_env.globals['momentjs'] = MomentJS


def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


babel = Babel(app)
babel.init_app(app, locale_selector=get_locale)

from app import views, models

# if not app.debug:
#     import logging
#     from logging.handlers import RotatingFileHandler
#     file_handler = RotatingFileHandler('tmp/custom-log.log', 'a', 1 * 1024 * 1024, 10)
#     file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     app.logger.setLevel(logging.INFO)
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
#     app.logger.info('custom-blog startup')
