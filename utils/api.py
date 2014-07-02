# coding:utf-8

from flask import render_template, request, abort, jsonify, g
from flask.views import MethodView

from werkzeug.datastructures import ImmutableMultiDict

from utils import check_status, serialize_pagination
from utils.decorators import authenticated
from utils.models import SeenModel

from wtforms.validators import ValidationError

import datetime
import json


class LEVELS(object): #Enum
    CLIENT = 0
    MEMBER = 1
    ADMIN = 2

class BaseAPI(MethodView):
    """
    /
        GET - List all items present, based on params
        POST - Create a new item

    /<id>
        GET - Return the queried item
        PUT - Update the queried item
        PATCH - alias of PUT
        DELETE - Delete the queried item
    """

    @classmethod
    def register(cls, mod, url='/', key_name='id', key_type='int', actions = ['list', 'details', 'create', 'update', 'delete']):
        f = cls.as_view(mod.name)

        cls.key_name = key_name

        if 'list' in actions: mod.add_url_rule(url, view_func=f, methods=['GET'])
        if 'create' in actions: mod.add_url_rule(url, view_func=f, methods=['POST'])
        if 'details' in actions: mod.add_url_rule('%s<%s:%s>' % (url, key_type, key_name), view_func=f, methods=['GET'])
        if 'update' in actions: mod.add_url_rule('%s<%s:%s>' % (url, key_type, key_name), view_func=f, methods=['PUT', 'PATCH'])
        if 'delete' in actions: mod.add_url_rule('%s<%s:%s>' % (url, key_type, key_name), view_func=f, methods=['DELETE'])

    @authenticated
    def get(self, **kwargs):
        if self.key_name in kwargs:
            return self.details(**kwargs)
        else:
            return self.list(**kwargs)

    def list(self, **kwargs):
        if self.check_read_access('list', **kwargs) == False:
            return abort(403)

        form = self.form_listing(request.args)

        if not form.validate():
            return form.errors_as_json()

        pagination = self.model.find(form, **kwargs)
        return serialize_pagination(pagination), 200

    def details(self, **kwargs):
        if self.check_read_access('details', **kwargs) == False:
            return abort(403)

        instance = getattr(self.model, 'find_by_%s' % self.key_name)(**kwargs)
        check_status(instance)

        result = instance.to_json()

        if isinstance(instance, SeenModel):
            if not instance.seen:
                instance.seen = 0

            instance.seen = instance.seen + 1
            instance.last_seen = datetime.datetime.utcnow()
            instance.save()

        return jsonify(result), 200

    @authenticated
    def post(self, **kwargs):
        if self.check_write_access('create', **kwargs) == False:
            return abort(403)

        if not self.form:
            return abort(405)

        # If already exists, 409 (conflict)
        if len(request.form) > 0:
            form = self.form(request.form)
        else:
            form = self.form(ImmutableMultiDict(request.json))

        if not form.validate():
            return form.errors_as_json()

        try:
            self.pre_create(form, **kwargs)
        except FormApiError, e:
            if not e.get_key() in form.errors:
                form.errors[e.get_key()] = []

            form.errors[e.get_key()].append(e.get_message())
            return form.errors_as_json()

        data = self.get_form_as_dict(form, action='create', **kwargs)

        instance = self.model.create(form=None, **data)
        self.post_create(form, instance, **kwargs)

        instance.save()

        return jsonify(instance.to_json()), 201

    def patch(self, **kwargs):
        return self.put(**kwargs)

    @authenticated
    def put(self, **kwargs):
        if self.check_write_access('update', **kwargs) == False:
            return abort(403)

        if not self.form:
            return abort(405)

        instance = getattr(self.model, 'find_by_%s' % self.key_name)(**kwargs)
        check_status(instance)

        if len(request.form) > 0:
            form = self.form(request.form, obj=instance)
        else:
            form = self.form(ImmutableMultiDict(request.json), obj=instance)
        
        if not form.validate():
            return form.errors_as_json()

        try:
            self.pre_update(form, instance, **kwargs)
        except FormApiError, e:
            if not e.get_key() in form.errors:
                form.errors[e.get_key()] = []

            form.errors[e.get_key()].append(e.get_message())
            return form.errors_as_json()

        data = self.get_form_as_dict(form, action='update', **kwargs)

        instance = instance.update(form=None, **data)
        if hasattr(instance, 'modified'):
            instance.modified = datetime.datetime.utcnow()
            
        self.post_update(form, instance, **kwargs)

        instance.save()

        return jsonify(instance.to_json()), 200

    @authenticated
    def delete(self, **kwargs):
        if self.check_write_access('delete', **kwargs) == False:
            return abort(403)

        if not self.form:
            return abort(405)

        # Return 204 !
        instance = self.model.find_by_id(**kwargs)
        check_status(instance)

        try:
            self.pre_delete(instance, **kwargs)
        except FormApiError, e:
            if not e.get_key() in form.errors:
                form.errors[e.get_key()] = []

            form.errors[e.get_key()].append(e.get_message())
            return form.errors_as_json()

        instance.delete()
        self.post_delete(instance, **kwargs)

        return '', 204

    def check_read_access(self, type, **kwargs):
        pass

    def check_write_access(self, type, **kwargs):
        pass

    def get_form_as_dict(self, form, action, **kwargs):
        return form.get_as_dict()

    def pre_create(self, form, **kwargs):
        pass

    def post_create(self, form, instance, **kwargs):
        pass

    def pre_update(self, form, instance, **kwargs):
        pass

    def post_update(self, form, instance, **kwargs):
        pass

    def pre_delete(self, instance, **kwargs):
        pass

    def post_delete(self, instance, **kwargs):
        pass


class FormApiError(ValidationError):
    """
    Raised when a validator fails to validate its input.
    """
    def __init__(self, key, message, *args, **kwargs):
        self.key = key
        ValueError.__init__(self, message, *args, **kwargs)

    def get_key(self):
        return self.key

    def get_message(self):
        return self.message
