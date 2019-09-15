from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import basedir
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
app.blog_name = 'Custom Blog'

db = SQLAlchemy(app)

import os
from flask_login import LoginManager
from config import basedir

lm = LoginManager()
lm.init_app(app)


from app.momentjs import MomentJS
app.jinja_env.globals['momentjs'] = MomentJS

from flask_babel import Babel
babel = Babel(app)

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
