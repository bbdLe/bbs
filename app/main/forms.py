#-*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User

class NameForm(FlaskForm):
    name = StringField("你是谁？", validators = [Required()])
    submit = SubmitField("提交")

class EditProfileForm(FlaskForm):
    name = StringField("姓名", validators = [Length(0, 64)])
    localtion = StringField("位置", validators = [Length(0, 64)])
    about_me = TextAreaField("介绍")
    submit = SubmitField("提交")

class PostForm(FlaskForm):
    body = PageDownField("你想说什么?", validators=[Required()])
    submit = SubmitField("提交")

class EditProfileAdminForm(FlaskForm):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    username = StringField("用户名", validators=[Required(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "用户名必须是英文或者数字结合_.")])
    confirmed = BooleanField("验证")
    role = SelectField("角色", coerce=int)
    name = StringField("真实用户名", validators=[Length(1, 64)])
    localtion = StringField("地址", validators=[Length(1, 64)])
    about_me = TextAreaField("介绍")
    submit = SubmitField("提交")

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email = filed.data).first():
            raise ValidationError("邮箱已经存在")

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username = field.data).first():
            raise ValidationError("用户名已经存在")

class CommentForm(FlaskForm):
    body = PageDownField("评论", validators=[Required()])
    submit = SubmitField("提交")
