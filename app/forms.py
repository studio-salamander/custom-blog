import re

from flask_wtf import FlaskForm as BaseForm
from wtforms import PasswordField, BooleanField, TextAreaField, HiddenField, StringField
from wtforms.validators import Email, EqualTo, Length, Regexp, DataRequired

from app.models import User

_title_re = re.compile(r'[\t!"#$%&\'()*\-/<=>?@\[\\\]^_`{|};:,.]+')


class LoginForm(BaseForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(BaseForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', [DataRequired(), EqualTo('cpassword', message='Passwords must match')])
    cpassword = PasswordField('cpassword')


class EditForm(BaseForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        BaseForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self, extra_validators=None):
        if not BaseForm.validate(self):
            return False

        if self.nickname.data == self.original_nickname:
            return True

        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(
                'This nickname has invalid characters. Please use letters, numbers, dots and underscores only')
            return False

        usr = User.query.filter_by(nickname=self.nickname.data).first()
        if usr:
            self.nickname.errors.append('This nickname is already in use. Please choose another one')
            return False
        return True


class PostForm(BaseForm):
    # re.compile(r'^[-a-zA-Z0-9_]{2,}$')
    id = HiddenField('id', default=0)
    title = StringField('title', validators=[DataRequired(), Regexp(re.compile(r'^[-a-zA-Z0-9!?`" ()]{2,}$'),
                                                                    message='The title has a forbidden symbols')])
    slug = StringField('slug', validators=[Length(min=0, max=80)])
    body = TextAreaField('body', validators=[DataRequired(), Length(min=10, max=140)])
