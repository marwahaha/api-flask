# coding:utf-8

from utils.forms import BaseForm, BaseFilter, DateFilterField, LikeFilterLength, TimestampField, OptionalUrl
from wtforms import StringField, IntegerField, BooleanField, DateTimeField, TextAreaField, SelectField, validators, ValidationError

from members.models import Member

class MemberListing(BaseFilter):
    __orders__ = ('display', 'seen', 'last_seen', 'created', 'modified', 'country', 'status', 'owner', 'sector')

    project_id = IntegerField()
    display = StringField(validators=[LikeFilterLength()])
    email = StringField(validators=[LikeFilterLength()])
    sector = StringField(validators=[LikeFilterLength()])
    owner_id = IntegerField()
    country = StringField(validators=[LikeFilterLength()])
    status = StringField(validators=[LikeFilterLength()])
    created = DateFilterField()
    removed = BooleanField(false_values=('False', '0', '', 'false', False))


class MemberForm(BaseForm):
    display = StringField(validators=[validators.DataRequired()])
    email = StringField(default=None, validators=[validators.Optional(), validators.Email()], filters = [lambda x: x or None])
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



class MemberCommentListing(BaseFilter):
    __orders__ = ('created', 'author', 'client')

    created = DateFilterField()
    author_id = IntegerField()
    client_id = IntegerField()

class MemberCommentForm(BaseForm):
    message = StringField(validators=[validators.DataRequired()])
