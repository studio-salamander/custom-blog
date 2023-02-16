import re
from hashlib import md5

from flask_login import UserMixin

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|};:,.]+')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(100))
    nickname = db.Column(db.String(100), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def __init__(self, email, password, nickname, role):
        self.email = email
        self.password = password
        self.nickname = nickname
        self.role = role

    def __repr__(self):
        return f'<User {self.email}>'

    def avatar(self, size):
        digest = md5(self.email.encode('utf8')).hexdigest()
        return f'http://www.gravatar.com/avatar/{digest}?d=mm&s={str(size)}'

    @staticmethod
    def make_unique_nickname(nickname, uid):
        user = User.query.get(uid)
        if not User.query.filter_by(nickname=nickname).first() or user.nickname == nickname:
            return nickname

        version = 2
        while True:
            new_nickname = nickname + str(version)
            if not User.query.filter_by(nickname=new_nickname).first():
                break

            version += 1

        return new_nickname

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub(r'[^a-zA-Z0-9_\.]', '', nickname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(80))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'

    @staticmethod
    def slugify(text, delimiter='-'):
        result = []
        for word in _punct_re.split(text.lower()):
            # word = normalize('NFKD', word).encode('ascii', 'ignore')
            if word:
                result.append(word)

        return delimiter.join(result)

    @staticmethod
    def make_unique_slug(slug, pid=0):
        if not Post.query.filter_by(slug=slug).first():
            return slug

        if pid:
            post = Post.query.get(pid)
            if post.slug == slug:
                return slug

        version = 2
        while True:
            new_slug = slug + str(version)
            if not Post.query.filter_by(slug=new_slug).first():
                break

            version += 1

        return new_slug
