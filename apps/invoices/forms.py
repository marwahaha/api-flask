# coding:utf-8

from utils.forms import BaseForm, BaseFilter, DateFilterField, LikeFilterLength, TimestampField, NullableIntegerField
from wtforms import StringField, IntegerField, BooleanField, DecimalField, SelectField, TextAreaField, validators, ValidationError

from projects.models import Project
from members.models import Member

class InvoiceListing(BaseFilter):
    __orders__ = ('display', 'reference', 'project', 'client', 'created', 'due')

    project_id = IntegerField(filters = [lambda x: x or None])
    client_id = IntegerField(filters = [lambda x: x or None])
    amount = DecimalField(filters = [lambda x: x or None], validators=[validators.Optional()])
    status = SelectField(choices=[(None, ''), ('DRAFT', 'DRAFT'), ('APPROVED', 'APPROVED'), ('LATE', 'LATE'), ('PAID', 'PAID'), ('PARTIALLY', 'PARTIALLY'), ('OVERPAID', 'OVERPAID')], filters = [lambda x: x or None], validators=[validators.Optional()])
    display = StringField(validators=[LikeFilterLength()])
    reference = StringField(validators=[LikeFilterLength()])
    currency = StringField(validators=[LikeFilterLength()])
    created = DateFilterField(filters = [lambda x: x or None])
    due = DateFilterField(filters = [lambda x: x or None])
    removed = BooleanField(false_values=('False', '0', '', 'false', False))


class InvoiceForm(BaseForm):
    reference = StringField(validators=[validators.DataRequired()])

    created = TimestampField(filters = [lambda x: x or None])
    due = TimestampField(filters = [lambda x: x or None])
    removed = TimestampField(filters = [lambda x: x or None])

    project_id = NullableIntegerField(filters = [lambda x: x or None])
    client_id = NullableIntegerField(filters = [lambda x: x or None])
    currency = StringField(filters = [lambda x: x or None])

    message = TextAreaField(filters = [lambda x: x or None])
    tax = DecimalField(filters = [lambda x: x or None])

    discount = DecimalField(filters = [lambda x: x or None])
    discount_percent = BooleanField(false_values=('False', '0', '', 'false', False))

    def validate_project_id(form, field):
        if not field.data:
            return

        if field.data:
            project = Project.find_by_id(field.data)
            if not project:
                raise ValidationError('Project not found.')

    def validate_client_id(form, field):
        if not field.data:
            return

        member = Member.find_by_id(field.data)
        if not member:
            raise ValidationError('Client not found.')

class InvoiceEmail(BaseForm):
    name = StringField(validators=[validators.DataRequired()])
    email = StringField(validators=[validators.DataRequired(), validators.Email()])
    subject = StringField(validators=[validators.DataRequired()])
    message = TextAreaField(validators=[validators.DataRequired()])

class InvoiceEntryListing(BaseFilter):
    __orders__ = ('amount', 'quantity', 'id',  'optional', 'sort')

    description = StringField(validators=[LikeFilterLength()])
    amount = DecimalField(filters = [lambda x: x or None])
    quantity = IntegerField(filters = [lambda x: x or None])
    optional = BooleanField(false_values=('False', '0', '', 'false', False), filters = [lambda x: x or None])


class InvoiceEntryForm(BaseForm):
    description = StringField(validators=[validators.DataRequired()])
    amount = DecimalField(validators=[validators.DataRequired()])
    quantity = IntegerField(validators=[validators.DataRequired()])

    optional = BooleanField(false_values=('False', '0', '', 'false', False))
    sort = IntegerField()

class InvoiceItemListing(BaseFilter):
    __orders__ = ('amount', 'id',  'optional')

    description = StringField(validators=[LikeFilterLength()])
    amount = DecimalField(filters = [lambda x: x or None])
    optional = BooleanField(false_values=('False', '0', '', 'false', False), filters = [lambda x: x or None])


class InvoiceItemForm(BaseForm):
    description = StringField(validators=[validators.DataRequired()])
    amount = DecimalField(validators=[validators.DataRequired()])

    optional = BooleanField(false_values=('False', '0', '', 'false', False))


class InvoicePaymentListing(BaseFilter):
    __orders__ = ('amount', 'paid', 'created')

    amount = DecimalField()
    created = DateFilterField()
    paid = DateFilterField()


class InvoicePaymentForm(BaseForm):
    amount = DecimalField(validators=[validators.DataRequired()])
    paid = TimestampField(validators=[validators.DataRequired()])
