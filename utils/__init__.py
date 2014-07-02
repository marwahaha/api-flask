# coding:utf-8

from utils.models import RemovableModel
from flask import abort, jsonify

def check_status(model):
    if model is None:
        abort(404)
    elif isinstance(model, RemovableModel) and model.removed is not None:
        abort(410)

    return None

def serialize_pagination(pagination):
    return jsonify({
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'items': [i.to_json() for i in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total
    })
