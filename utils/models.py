# coding:utf-8

from database import db
import datetime

from flask_wtf import Form
from wtforms import StringField, SelectField
from utils.forms import BaseFilter, OrderByTextField, DateFilterField

class RemovableModel(object):
    pass

class SeenModel(object):
    pass

class JsonSerializable(object):
    __jsonserialize__ = ['id', ('__repr__', 'display')]
    UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

    def simple_serializer(self, item):
        if hasattr(item, '__serialize__'):
            return getattr(item, '__serialize__')()

        return {'id': item.id, 'display': item.__repr__()}

    def to_json(self):
        if hasattr(self.__jsonserialize__, '__call__'):
            return self.__jsonserialize__()
        
        json = {}
        columns = self.__jsonserialize__

        for column in columns:
            key = column

            if isinstance(column, tuple):
                key = column[1]
                column = column[0]

            prop = getattr(self, column, None)

            if hasattr(prop, '__call__'):
                # In case we want to serialize a method
                try:
                    json[key] = prop()
                except:
                    pass
            elif isinstance(prop, db.Model):
                # if a model, we simple serialize it
                json[key] = self.simple_serializer(prop)

            elif isinstance(prop, list):
                # Can be a list of direct item, or a list from a m2m
                # If it's a direct item, we go for it
                # If it's a m2m, we get the details of the related object
                json[key] = []
                for item in prop:
                    json[key].append(self.simple_serializer(item))

            elif isinstance(prop, datetime.datetime):
                # In case of a date, we output a timestamp
                json[key] = int((prop - self.UNIX_EPOCH).total_seconds() * 1000)
            else:
                json[key] = prop

        return json

class ModelForm(object):
    @classmethod
    def paginate(cls, query, form):
        if not isinstance(form, BaseFilter):
            raise Exception("{0} is not a BaseFilter form".format(form))

        return query.paginate(form.page.data, form.limit.data, False)

    @classmethod
    def _query_filter(cls, query, column, field):
        # Implementing like if present
        if isinstance(field, StringField):
            return query.filter(column.ilike(field.data + '%'))

        # Implementing multiple date if required
        elif isinstance(field, DateFilterField):
            values = field.get_as_list()
            for operator, value in values:
                if operator == "eq":
                    query = query.filter(column == value)
                elif operator == "ne":
                    query = query.filter(column != value)
                elif operator == "lt":
                    query = query.filter(column < value)
                elif operator == "gt":
                    query = query.filter(column > value)
                elif operator == "le":
                    query = query.filter(column <= value)
                elif operator == "ge":
                    query = query.filter(column >= value)
                elif operator == "in":
                    query = query.filter(column.in_(list(value)))
                elif operator == "ni":
                    query = query.filter(column.notin_(list(value)))

            return query

        # Special case with removable
        elif field.name == 'removed' and issubclass(column.class_, RemovableModel):
            if field.data:
                return query.filter(column != None)
            else:
                return query.filter(column == None)

        # If nothing has to be done
        else:
            if not field.data or field.data == 'None':
                return query

            return query.filter(column == field.data)

    @classmethod
    def _query_order_by(cls, query, order_by):
        if order_by:
            for k in order_by:
                if hasattr(cls, 'order_by_%s' % (k[0],)):
                    query = getattr(cls, 'order_by_%s' % (k[0],))(query, k[1].lower())
                else:
                    query = query.order_by(getattr(getattr(cls, k[0]), k[1].lower())())

        return query

    @classmethod
    def query_from_base_filter(cls, form):
        if not isinstance(form, BaseFilter):
            raise Exception("{0} is not a BaseFilter form".format(form))

        query = cls.query
        for name in form._fields:
            if name in ("csrf_token", "limit", "page", "order_by"): continue

            field = getattr(form, name)
            if isinstance(field, DateFilterField):
                data = field.get_as_list()
            else:
                data = field.data

            if data is None or data == "": continue

            if hasattr(cls, "filter_by_%s" % (field.name,)):
                query = getattr(cls, "filter_by_%s" % (field.name,))(query, field)
            else:
                query = cls._query_filter(query, getattr(cls, field.name), field)

        query = cls._query_order_by(query, form.order_by.get_as_list())

        return query

    @classmethod
    def create(cls, form=None, **kwargs):
        if form:
            if not isinstance(form, Form):
                raise Exception("Given form \"{0}\" in ModelForm must be an instance of wtforms.Form".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        instance = cls(**kwargs)
        return instance

    def update(self, form=None, **kwargs):
        if form:
            if not isinstance(form, Form):
                raise Exception("Given form \"{0}\" in ModelForm must be an instance of wtforms.Form".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

        return self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


import sqlalchemy.types as types

class DbAmount(types.TypeDecorator):
    impl = types.Integer
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.Integer)
    def process_bind_param(self, value, dialect):
        if not value:
            return None

        return value * 100
    def process_result_value(self, value, dialect):
        if not value:
            return 0

        return float("{:.2f}".format(float(value)/100))