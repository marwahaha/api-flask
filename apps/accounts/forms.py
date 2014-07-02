# coding:utf-8

from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SelectField, validators, ValidationError
from utils.forms import TimestampField, OptionalUrl
from members.forms import MemberForm
from members.models import Member

class AccountForm(MemberForm):
    display = StringField(validators=[validators.DataRequired()])
    email = StringField(default=None, validators=[validators.DataRequired(), validators.Email()], filters = [lambda x: x or None])
    password = PasswordField(validators=[validators.Optional(), validators.EqualTo('confirm', message='Passwords must match')], filters = [lambda x: x or None])
    confirm  = PasswordField(validators=[validators.Optional()], filters = [lambda x: x or None])
    address = TextAreaField(filters = [lambda x: x or None])
    office = StringField(filters = [lambda x: x or None])
    mobile = StringField(filters = [lambda x: x or None])
    fax = StringField(filters = [lambda x: x or None])
    website = StringField(validators=[OptionalUrl()], filters = [lambda x: x or None])
    description = TextAreaField(filters = [lambda x: x or None])
    sector = StringField(filters = [lambda x: x or None])
    lang = StringField(validators=[validators.Optional(), validators.Length(min=2,max=2)], filters = [lambda x: x or None])
    removed = TimestampField(filters = [lambda x: x or None])
    owner_id = IntegerField(filters = [lambda x: x or None])
    status = SelectField(choices=[('CLIENT', 'CLIENT'), ('MEMBER', 'MEMBER')], validators=[validators.DataRequired()])

    def validate_owner_id(form, field):
        if field.data:
            member = Member.find_by_id(field.data)
            if not member:
                raise ValidationError('Member (owner) was not found.')