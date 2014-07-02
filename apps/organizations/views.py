# coding:utf-8

from flask import Blueprint, jsonify, abort, request, g
from utils.api import BaseAPI, FormApiError, LEVELS

from .forms import OrganizationForm, OrganizationCreateForm
from .models import Organization

from base.models import Application, ApplicationPlan
from members.models import Member

import bcrypt


class OrganizationAPI(BaseAPI):
    def __init__(self):
        self.form_listing = None
        self.form = OrganizationForm
        self.model = Organization

    def check_write_access(self, type, **kwargs):
        if not g.member.admin:
            abort(403)

    def pre_update(self, form, instance, name):
        plan = ApplicationPlan.find_by_id(form.application_plan_id.data)
        if not plan:
            raise FormApiError('application_plan_id', 'No application plan found..')

        if form.name.data != instance.name:
            check = Organization.query.filter(Organization.name == form.name.data).first()
            if check:
                raise FormApiError('name', 'Name is already taken.')


app = Blueprint('organizations', __name__)
OrganizationAPI.register(app, '/', key_name="name", key_type="string", actions=['details', 'update', 'delete'])

@app.route('/', methods=['POST'])
def create():
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

    form = OrganizationCreateForm(request.form)
    if not form.validate():
        return form.errors_as_json()

    plan = ApplicationPlan.find_by_id(form.application_plan_id.data)
    if not plan:
        form.errors['application_plan_id'] = ['No application plan found..']
        return form.errors_as_json()

    check = Organization.query.filter(Organization.name == form.name.data).first()
    if check:
        form.errors['name'] = ['Name is already taken.']
        return form.errors_as_json()

    organization = Organization(**{
        'name': form.name.data,
        'display': form.display.data,
        'description': form.description.data,
        'website': form.description.data,
        'removed': form.removed.data,
        'currency': form.currency.data.upper(),
        'application_plan_id': form.application_plan_id.data,
        'application_id': g.application.id
    })
    organization.save()

    member = Member(**{
        'display': Member.display_from_email(form.member_email.data),
        'email': form.member_email.data,
        'password': bcrypt.hashpw(form.member_password.data, bcrypt.gensalt()),
        'organization_id': organization.id,
        'status': 'MEMBER',
        'admin': True
    })

    member.save()

    return jsonify(organization.to_json()), 201
