# coding:utf-8

from flask import jsonify
from flask_wtf import Form
from wtforms import IntegerField, StringField, SelectMultipleField
from wtforms.validators import ValidationError, NumberRange, URL
from wtforms import widgets
import datetime

class OrderByTextField(SelectMultipleField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `rows`
    attribute to the select field when rendering.
    """
    widget = widgets.Select(multiple=True)
    coerce = str

    def __init__(self, choices=[], **kwargs):
        self.choices = choices
        SelectMultipleField.__init__(self, **kwargs)


    def get_as_list(self):
        """
        Returns the parameters as a list of (column, ordering)
        with ordering being ASC (default) or DESC
        """
        if not self.data:
            return None

        ordering = []
        for d in self.data:
            way = 'ASC'
            column = d
            if d[0:1] == '-':
                way = 'DESC'
                column = d[1:]

            ordering.append((column, way))

        if len(ordering) > 0:
            return ordering

        return None

    def pre_validate(self, form):
        if form.__orders__ is None:
            return

        if self.data is None:
            return

        for d in self.data:
            if d[0:1] in ('-', '+'):
                d = d[1:]

            if d not in form.__orders__:
                raise ValueError(self.gettext(u"'%(value)s' is not a valid choice for this field") % dict(value=d))


class DateFilterField(SelectMultipleField):
    """
    Accepts one or two dates that can start with <, >, <=, >=, = (default)
    """
    widget = widgets.Select(multiple=True)
    coerce = str
    choices = []
    alloweds = ('lt', 'gt', 'le', 'ge', 'eq', 'ne')

    def __init__(self, maximum=5, **kwargs):
        SelectMultipleField.__init__(self, **kwargs)
        self.maximum = maximum

    def get_as_list(self):
        """
        Returns data as dict of list (operator, value)
        Will match multiple equals to "in" operator, and multiple not_equals to ni (not_in) operator
        """
        filters = []
        equals = 0     # Used to populate a "in" field
        not_equals = 0 # Used to populate a "ni" field (not in)

        if not self.data:
            return None

        for d in self.data:
            if d == '':
                continue

            operator = 'eq'
            value = d
            if d[0:2] in self.alloweds:
                operator = d[0:2]
                value = d[2:]

            if operator == 'eq':
                equals += 1
            elif operator == 'ne':
                not_equals +=1


            filters.append((operator, datetime.datetime.utcfromtimestamp(long(value)/1000.0)))

        if equals > 1 or not_equals > 1:
            new_filters = []
            in_filter = []
            not_in_filter = []
            for operator, value in filters:
                if operator == 'eq' and equals > 1:
                    if value not in in_filter:
                        in_filter.append(value)
                elif operator == 'ne' and not_equals > 1:
                    if value not in not_in_filter:
                        not_in_filter.append(value)
                else:
                    new_filters.append((operator, value))

            if equals > 1:
                if len(in_filter) > 1:
                    new_filters.append(('in', tuple(in_filter)))
                else:
                    new_filters.append(('eq', in_filter[0]))
            if not_equals > 1:
                if len(not_in_filter) > 1:
                    new_filters.append(('ni', tuple(not_in_filter)))
                else:
                    new_filters.append(('ne', not_in_filter[0]))

            filters = new_filters

        if len(filters) > 0:
            return filters

        return None

    def pre_validate(self, form):
        if self.data is None:
            return

        if len(self.data) > self.maximum:
            raise ValueError(self.gettext(u"Field must contains a maximum of %(max)d entries.") % dict(max=self.maximum))

        for d in self.data:
            if d == '':
                continue

            operator = d[0:2]
            if not operator.isdigit():
                if operator in self.alloweds and d[2:].isdigit():
                    continue
            else:
                if d.isdigit():
                    continue

            raise ValueError(self.gettext(u"Invalid value. Must be a timestamp, or two chars for the operator followed by a timestamp."))


class LikeFilterLength(object):
    def __init__(self, min=3, message=None):
        self.min = min
        if not message:
            message = u'Field must be at least %i characters long.' % (self.min,)
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            return

        if field.data[:1] == '%' or field.data[-1:] == '%':
            if len(field.data) < self.min:
                raise ValidationError(self.message)


class TimestampField(IntegerField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            try:
                self.data = datetime.datetime.utcfromtimestamp(long(valuelist[0])/1000.0)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid timestamp value'))


class BaseForm(Form):
    def errors_as_json(self):
        return jsonify(self.errors), 400

    def get_as_dict(self):
        results = {}
        for key in self._fields:
            if 'csrf_token' == key: continue
            results[key] = getattr(self, key).data

        return results

class BaseFilter(BaseForm):
    __orders__ = None
    limit = IntegerField('limit', default=10)
    page = IntegerField('page', validators=[NumberRange(min=1)], default=1)
    order_by = OrderByTextField('order_by')

    def validate_limit(form, field):
        if field.data == 0: # For querying only total
            pass
        elif field.data != 0 and field.data >= 5 and field.data <= 50:
            pass
        else:
            raise ValidationError(field.gettext('Number must be either 0 or between %(min)s and %(max)s.') % dict(min=5, max=50))

class NullableIntegerField(IntegerField):
    """
    An IntegerField where the field can be null if the input data is an empty
    string.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            if not valuelist[0] or valuelist[0] == '':
                self.data = None
            else:
                try:
                    self.data = int(valuelist[0])
                except ValueError:
                    self.data = None
                    raise ValueError(self.gettext('Not a valid integer value'))

class OptionalUrl(URL):
    def __call__(self, form, field):
        if not field.data:
            return

        super(OptionalUrl, self).__call__(form, field)