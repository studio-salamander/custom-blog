import os

# Security
WTF_CSRF_ENABLED = True
SECRET_KEY = 'xnj-nj-tcnm-e-tutvjnf'

# SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

DB_PATH = os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# available languages
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский'
}
