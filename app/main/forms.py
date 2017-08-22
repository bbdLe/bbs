#-*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField("你是谁？", validators = [Required()])
    submit = SubmitField("提交")
