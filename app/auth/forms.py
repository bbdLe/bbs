#-*- coding: utf-8 -*-
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    password = PasswordField("密码", validators=[Required()])
    remember_me = BooleanField("保持登陆")
    submit = SubmitField("登陆")

class ChangePasswordForm(Form):
    oldpassword = PasswordField("旧密码", validators=[Required()])
    newpassword = PasswordField("新密码", validators=[Required(), EqualTo("newpassword2", message="密码必须相同")])
    newpassword2 = PasswordField("再次输入新密码", validators=[Required()])
    submit = SubmitField("确认")

class SendMailResetPasswordForm(Form):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField("确定")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("该邮箱不存在")

class ResetPasswordForm(Form):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    password = PasswordField("新密码", validators=[Required(), EqualTo("password2", message="密码必须相同")])
    password2 = PasswordField("再次输入密码", validators=[Required()])
    submit = SubmitField("确定")

class RegistrationForm(Form):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    username = StringField("用户名", validators=[Required(), Length(1, 64),
                                                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, "用户名只能是英文,数字，下划线，点号")])
    password = PasswordField("密码", validators=[Required(), EqualTo('password2', message="密码必须相同")])
    password2 = PasswordField("再次输入密码", validators=[Required()])
    name = StringField("姓名", validators=[Length(0,64)])
    localtion = StringField("地址", validators=[Length(0, 64)])
    about_me = TextAreaField("简介")
    submit = SubmitField("注册")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已经被注册")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已经被注册")
