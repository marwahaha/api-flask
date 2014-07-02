# coding:utf-8

from flask import Blueprint, g, jsonify
from flask import render_template, request

from .models import *
from .forms import *

from base.models import Application

app = Blueprint('auth', __name__)


@app.route('/login', methods=['POST'])
def login():
    from members.models import Profile

    if 'app-key' not in request.headers:
        response = jsonify({'code': 401, 'message': 'App-Key header is required.'})
        response.status_code = 401
        return response

    application = Application.find_by_key(request.headers['app-key'])
    if not application:
        response = jsonify({'code': 401, 'message': 'Invalid App-key.'})
        response.status_code = 401
        return response

    g.application = application

    form = AuthenticationForm(request.form)
    if not form.validate():
        return form.errors_as_json()

    profile = Profile.find_by_email(form.email.data)
    if not profile:
        form.errors['email'] = ['Invalid password or account does not exists.']
        return form.errors_as_json()

    if not profile.check_passwd(form.password.data):
        form.errors['email'] = ['Invalid password or account does not exists.']
        return form.errors_as_json()

    session = Session(profile.id)
    session.save()

    return jsonify(session.to_json()), 200
