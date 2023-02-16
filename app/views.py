from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import render_template, flash, redirect, session, url_for, request, abort
from flask_babel import gettext
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, lm
from app.forms import LoginForm, RegisterForm, EditForm, PostForm
from app.models import User, ROLE_USER, Post


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


def redirect_url(default='index'):
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)


@app.errorhandler(401)
def not_found_error(error):
    return render_template('401.html',
                           blog_name=app.blog_name,
                           title=gettext('Access Restricted')), 401


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
                           blog_name=app.blog_name,
                           title=gettext('File Not Found')), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',
                           blog_name=app.blog_name,
                           title=gettext('An unexpected error has occurred')), 500


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
# @login_required
def index():
    usr = ''
    if current_user.is_authenticated:
        usr = current_user
    posts = Post.query.filter(id != 0).order_by(desc('timestamp'))
    return render_template("index.html",
                           blog_name=app.blog_name,
                           title=gettext('Home'),
                           user=usr,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', nickname=current_user.nickname))

    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=form.email.data).first()
        if usr is None or not check_password_hash(usr.password, form.password.data):
            flash(gettext('Wrong credentials'))
            return redirect(url_for('login'))

        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(usr, remember=remember_me)
        flash(gettext('Logged in successfully'))

        nxt = request.args.get('next')
        if not is_safe_url(nxt):
            return abort(400)

        return redirect(nxt or url_for('index'))

    return render_template('login.html',
                           blog_name=app.blog_name,
                           title=gettext('Sign In'),
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user', nickname=current_user.nickname))

    form = RegisterForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=form.email.data).first()
        if usr is None:
            nickname = form.email.data.split('@')[0]
            nickname = User.make_valid_nickname(nickname)
            nickname = User.make_unique_nickname(nickname, 1)
            usr = User(email=form.email.data, password=generate_password_hash(form.password.data), nickname=nickname,
                       role=ROLE_USER)
            db.session.add(usr)
            db.session.commit()
        else:
            flash(gettext('Such user already is available'))
            return redirect(url_for('register'))

        flash(gettext('Registered successfully'))

        return redirect(url_for('login'))

    return render_template('register.html',
                           blog_name=app.blog_name,
                           title=gettext('Register'),
                           form=form)


@app.route('/user/<nickname>', methods=['GET', 'POST'])
# @login_required
def user(nickname):
    usr = User.query.filter_by(nickname=nickname).first()
    if not usr:
        flash(f'User {nickname} not found')
        return redirect(url_for('index'))

    # if current_user.is_authenticated and user.id != current_user.id:
    #     flash('Access Restricted')
    #     return redirect(redirect_url())

    form = PostForm()
    if form.validate_on_submit():
        slug = Post.make_unique_slug(form.slug.data, form.id.data)
        if slug.strip() == '':
            slug = Post.slugify(form.title.data)

        pst = Post(title=form.title.data, slug=slug, body=form.body.data, timestamp=datetime.utcnow(), author=usr)
        db.session.add(pst)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(redirect_url())

    posts = Post.query.filter_by(author=usr).order_by(desc('timestamp'))

    return render_template('user.html',
                           blog_name=app.blog_name,
                           title=gettext('Profile'),
                           user=usr,
                           form=form,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    usr = current_user
    form = EditForm(current_user.nickname)
    if form.validate_on_submit():
        nickname = User.make_valid_nickname(form.nickname.data)
        nickname = User.make_unique_nickname(nickname, usr.id)
        current_user.nickname = nickname
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(gettext('Your changes have been saved'))
        return redirect(url_for('user', nickname=current_user.nickname))
    else:
        form.nickname.data = current_user.nickname
        form.about_me.data = current_user.about_me

    return render_template('edit.html',
                           blog_name=app.blog_name,
                           title=gettext('Edit Profile'),
                           user=usr,
                           form=form)


@app.route('/update/<post_id>', methods=['GET', 'POST'])
@login_required
def update(post_id):
    form = PostForm()
    posts = Post.query.filter_by(author=current_user).order_by(desc('timestamp'))
    if form.validate_on_submit():
        slug = Post.make_unique_slug(form.slug.data, post_id)
        if not slug.strip():
            slug = Post.slugify(form.title.data)

        pst = Post.query.get(form.id.data)
        pst.title = form.title.data
        pst.slug = slug
        pst.body = form.body.data
        pst.timestamp = datetime.utcnow()
        db.session.commit()
        flash(gettext('Your post is updated!'))

        return redirect(url_for('user', nickname=current_user.nickname))

    else:
        pst = Post.query.get(post_id)
        if not pst:
            flash(gettext('Post not found'))
            return redirect(redirect_url())

        if pst.author.id != current_user.id or not current_user.is_authenticated:
            flash(gettext('You cannot update this post'))
            return redirect(redirect_url())

    form.id.data = post_id
    if not form.title.data:
        form.title.data = pst.title
        form.slug.data = pst.slug
        form.body.data = pst.body
    else:
        form.title.data = form.title.data
        form.slug.data = form.slug.data
        form.body.data = form.body.data

    return render_template('user.html',
                           blog_name=app.blog_name,
                           title=gettext('Profile'),
                           user=current_user,
                           form=form,
                           posts=posts)


@app.route('/delete/<post_id>')
@login_required
def delete(post_id):
    pst = Post.query.get(post_id)
    back = url_for('user', nickname=pst.author.nickname)
    if not pst:
        flash(gettext('Post not found'))
        return redirect(back)

    if pst.author.id != current_user.id or not current_user.is_authenticated:
        flash(gettext('You cannot delete this post'))
        return redirect(back)

    db.session.delete(pst)
    db.session.commit()
    flash(gettext('Your post has been deleted'))
    return redirect(back)


@app.route('/<slug>', methods=['GET'])
def post(slug):
    pst = Post.query.filter_by(slug=slug).first()
    if not pst:
        flash(gettext('Post not found'))
        return redirect(redirect_url())

    return render_template("single-post.html",
                           blog_name=app.blog_name,
                           title=gettext(pst.title),
                           user=current_user,
                           post=pst)
