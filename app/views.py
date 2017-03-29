from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from flask_babel import gettext
from app import app, db, lm, babel
from config import LANGUAGES
from app.forms import LoginForm, RegisterForm, EditForm, PostForm
from app.models import User, ROLE_USER, ROLE_ADMIN, Post
from werkzeug.security import generate_password_hash, check_password_hash

from urllib.parse import urlparse, urljoin
from datetime import datetime
from sqlalchemy import desc

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


@lm.user_loader
def get_user(ident):
  return User.query.get(int(ident))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()

def redirect_url(default = 'index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.errorhandler(401)
def not_found_error(error):
    return render_template('401.html',
        blog_name = app.blog_name,
        title = gettext('Access Restricted')), 401


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
        blog_name = app.blog_name,
        title = gettext('File Not Found')), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',
        blog_name = app.blog_name,
        title = gettext('An unexpected error has occurred')), 500


@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
# @login_required
def index():
    user = ''
    if current_user.is_authenticated:
        user = current_user
    posts = Post.query.filter(id != 0).order_by(desc('timestamp'))
    return render_template("index.html",
        blog_name = app.blog_name,
        title = gettext('Home'),
        user = user,
        posts = posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', nickname = current_user.nickname))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None or not check_password_hash(user.password, form.password.data):
            flash(gettext('Wrong credentials'))
            return redirect(url_for('login'))

        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
        flash(gettext('Logged in successfully'))

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('index'))

    return render_template('login.html',
        blog_name = app.blog_name,
        title = gettext('Sign In'),
        form = form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user', nickname = current_user.nickname))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            nickname = form.email.data.split('@')[0]
            nickname = User.make_valid_nickname(nickname)
            nickname = User.make_unique_nickname(nickname, 0)
            user = User(email = form.email.data, password = generate_password_hash(form.password.data), nickname = nickname, role = ROLE_USER)
            db.session.add(user)
            db.session.commit()
        else:
            flash(gettext('Such user already is avalable'))
            return redirect(url_for('register'))

        flash(gettext('Registered successfully'))

        return redirect(url_for('login'))

    return render_template('register.html',
        blog_name = app.blog_name,
        title = gettext('Register'),
        form = form)

@app.route('/user/<nickname>', methods = ['GET', 'POST'])
#@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found')
        return redirect(url_for('index'))

    # if current_user.is_authenticated and user.id != current_user.id:
    #     flash('Access Restricted')
    #     return redirect(redirect_url())

    form = PostForm()
    if form.validate_on_submit():
        slug = Post.make_unique_slug(form.slug.data, form.id.data)
        if slug.strip() == '':
            slug = Post.slugify(form.title.data)
        post = Post(title = form.title.data, slug = slug, body = form.body.data, timestamp = datetime.utcnow(), author = user)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(redirect_url())

    posts = Post.query.filter_by(author = user).order_by(desc('timestamp'))

    return render_template('user.html',
        blog_name = app.blog_name,
        title = gettext('Profile'),
        user = user,
        form = form,
        posts = posts)


@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    user = current_user
    form = EditForm(current_user.nickname)
    if form.validate_on_submit():
        nickname = User.make_valid_nickname(form.nickname.data)
        nickname = User.make_unique_nickname(nickname, user.id)
        current_user.nickname = nickname
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(gettext('Your changes have been saved'))
        return redirect(url_for('user', nickname = current_user.nickname))
    else:
        form.nickname.data = current_user.nickname
        form.about_me.data = current_user.about_me
    return render_template('edit.html',
        blog_name = app.blog_name,
        title = gettext('Edit Profile'),
        user = user,
        form = form)


@app.route('/update/<int:id>', methods = ['GET', 'POST'])
@login_required
def update(id):
    form = PostForm()
    posts = Post.query.filter_by(author = current_user).order_by(desc('timestamp'))
    if form.validate_on_submit():
        slug = Post.make_unique_slug(form.slug.data, id)
        if slug.strip() == '':
            slug = Post.slugify(form.title.data)

        post = Post.query.get(form.id.data)
        post.title = form.title.data
        post.slug = slug
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.commit()
        flash(gettext('Your post is updated!'))

        return redirect(url_for('user', nickname = current_user.nickname))

    else:
        post = Post.query.get(id)
        if post == None:
            flash(gettext('Post not found'))
            return redirect(redirect_url())

        if post.author.id != current_user.id or not current_user.is_authenticated:
            flash(gettext('You cannot update this post'))
            return redirect(redirect_url())

    form.id.data = id
    if form.title.data is None:
        form.title.data = post.title
        form.slug.data = post.slug
        form.body.data = post.body
    else:
        form.title.data = form.title.data
        form.slug.data = form.slug.data
        form.body.data = form.body.data

    return render_template('user.html',
        blog_name = app.blog_name,
        title = gettext('Profile'),
        user = current_user,
        form = form,
        posts = posts)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    back = url_for('user', nickname = post.author.nickname)
    if post == None:
        flash(gettext('Post not found'))
        return redirect(back)

    if post.author.id != current_user.id or not current_user.is_authenticated:
        flash(gettext('You cannot delete this post'))
        return redirect(back)

    db.session.delete(post)
    db.session.commit()
    flash(gettext('Your post has been deleted'))
    return redirect(back)


@app.route('/<slug>', methods = ['GET'])
def post(slug):
    post = Post.query.filter_by(slug = slug).first()
    if post == None:
        flash(gettext('Post not found'))
        return redirect(redirect_url())

    return render_template("single-post.html",
        blog_name = app.blog_name,
        title = gettext(post.title),
        user = current_user,
        post = post)
