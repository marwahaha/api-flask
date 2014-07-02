# coding:utf-8

from flask import Blueprint, g, jsonify
from flask import render_template, request

from werkzeug.datastructures import ImmutableMultiDict

from utils.decorators import authenticated

from .forms import AccountForm
from members.models import Profile

import datetime

app = Blueprint('accounts', __name__)

@app.route('')
@authenticated
def details():
    return jsonify(g.member.to_json()), 200

@app.route('', methods=['PUT'])
@authenticated
def update():
    if len(request.form) > 0:
        form = AccountForm(request.form, obj=g.member)
    else:
        form = AccountForm(ImmutableMultiDict(request.json), obj=g.member)
    
    if not form.validate():
        return form.errors_as_json()

    if not Profile.is_email_available(form.email.data, g.member.profile.id):
        form.errors['email'] = []

        form.errors['email'].append('This email is already taken.')
        return form.errors_as_json()

    g.member = g.member.update(form=None, **form.get_as_dict())
    if hasattr(g.member, 'modified'):
        g.member.modified = datetime.datetime.utcnow()

    g.member.profile.email = form.email.data
    if form.password.data:
    	g.member.profile.set_password(form.password.data)

    g.member.save()

    return jsonify(g.member.to_json()), 200