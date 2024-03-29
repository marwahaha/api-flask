# coding:utf-8

from utils.forms import BaseForm
from wtforms import StringField, PasswordField, validators


class AuthenticationForm(BaseForm):
    email = StringField(validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField(validators=[validators.DataRequired()])
