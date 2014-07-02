# coding:utf-8

from flask import request

from utils.forms import BaseForm, BaseFilter, DateFilterField, LikeFilterLength, TimestampField, OptionalUrl
from wtforms import StringField, IntegerField, BooleanField, DateTimeField, TextAreaField, SelectField, validators
from wtforms.validators import ValidationError

class ProjectListing(BaseFilter):
    __orders__ = ('display', 'start', 'due', 'created')

    display = StringField(validators=[LikeFilterLength()])
    member_id = IntegerField()
    start = DateFilterField()
    due = DateFilterField()
    created = DateFilterField()
    removed = BooleanField(false_values=('False', '0', '', 'false', False))


class ProjectForm(BaseForm):
    display = StringField(validators=[validators.DataRequired()])
    description = TextAreaField()
    website = StringField(validators=[OptionalUrl()])
    due = TimestampField()
    start = TimestampField()
    removed = TimestampField()


class ProjectMemberListing(BaseFilter):
    __orders__ = ('member')

    status = SelectField(validators=[validators.Optional(strip_whitespace=True)], choices=[('CLIENT', 'CLIENT'), ('MEMBER', 'MEMBER')])
    admin = BooleanField(false_values=('False', '0', '', 'false', False))


class ProjectMemberForm(BaseForm):
    member_id = IntegerField()
    application_plan_id = IntegerField()
    status = SelectField(validators=[validators.DataRequired()], choices=[('CLIENT', 'CLIENT'), ('MEMBER', 'MEMBER')])
    admin = BooleanField(false_values=('False', '0', '', 'false', False))

    def validate_member_id(form, field):
        from members.models import Member
        
        if request.method == 'POST':
            if not form.member_id.data:
                raise ValidationError(field.gettext('This field is required.'))

            field.member = Member.find_by_id(field.data)
            if not member:
                raise ValidationError('Member not found.')

        else:
            field.data = None

    def validate_application_plan_id(form, field):
        if form.status.data and form.status.data.lower() == 'member':
            if not field.data:
                raise ValidationError(field.gettext('This field is required.'))
