# coding:utf-8

from utils.forms import BaseForm, TimestampField, OptionalUrl
from wtforms import StringField, IntegerField, TextAreaField, SelectField, PasswordField, FormField, validators

import json

class OrganizationForm(BaseForm):
    name = StringField(validators=[validators.DataRequired(), validators.Regexp(u'^([a-z0-9_]{4,})$', message='Only alphanumerical and _ values.')])
    display = StringField(filters = [lambda x: x or None], validators=[validators.DataRequired()])
    description = TextAreaField(filters = [lambda x: x or None])
    website = StringField(validators=[OptionalUrl()], filters = [lambda x: x or None])
    business_number = StringField(filters = [lambda x: x or None])

    removed = TimestampField(filters = [lambda x: x or None])
    defaults = TextAreaField(filters = [lambda x: x or None])

    currency = SelectField(choices=[('USD', 'USD'), ('EUR', 'EUR')], validators=[validators.DataRequired()])
    application_plan_id = IntegerField(validators=[validators.DataRequired()])

    def validate_defaults(form, field):
        field.data = json.dumps(field.data)


class OrganizationCreateForm(BaseForm):
    name = StringField(validators=[validators.DataRequired()])
    display = StringField(validators=[validators.DataRequired()])
    description = TextAreaField(filters = [lambda x: x or None])
    website = StringField(validators=[OptionalUrl()], filters = [lambda x: x or None])

    removed = TimestampField(filters = [lambda x: x or None])

    currency = SelectField(choices=[('USD', 'USD'), ('EUR', 'EUR')], default='USD')
    application_plan_id = IntegerField(validators=[validators.DataRequired()])

    member_email = StringField(validators=[validators.DataRequired(), validators.Email()])
    member_password = PasswordField(validators=[validators.DataRequired(), validators.EqualTo('member_confirm', message='Passwords must match')])
    member_confirm  = PasswordField(validators=[validators.DataRequired()])
