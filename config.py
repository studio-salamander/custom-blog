# -*- coding: utf-8 -*-
# Security
WTF_CSRF_ENABLED = True
SECRET_KEY = 'xnj-nj-tcnm-e-tutvjnf'

# SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# available languages
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский'
}
