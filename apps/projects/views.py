# coding:utf-8

from flask import Blueprint, abort
from utils.api import BaseAPI, FormApiError

from .forms import *
from .models import *

import datetime


class ProjectAPI(BaseAPI):
    """
    listing :
        A client and member not admin can see all the projects he's in
        An admin can see all projects
    details :
        A client and member not admin can get details on project he's in
        An admin can see all projects
    create : Only admins
    update : Only admins
    delete : Only admins
    """

    def __init__(self):
        self.form_listing = ProjectListing
        self.form = ProjectForm
        self.model = Project

    def check_write_access(self, type, **kwargs):
        return g.member.admin

    def pre_create(self, form, **kwargs):
        if g.organization.application_plan.projects == 0:
            return

        projects = Project.count_projects()
        if g.organization.application_plan.projects <= projects:
            return abort(402)

    def post_create(self, form, instance):
        instance.application_id = g.application.id
        instance.created = datetime.datetime.utcnow()
        instance.organization_id = g.organization.id

    def post_delete(self, instance, id):
        from invoices.models import Invoice
        Invoice.query.filter(Invoice.project_id == instance.id).update({'project_id': None})

projects = Blueprint('projects', __name__)
ProjectAPI.register(projects, '/')

class ProjectMemberAPI(BaseAPI):
    """
    listing :
        A client and member not admin can see all members of a project if he's in the project
        An admin can see all the members in all the projects
    details :
        A client and member can get a details of the member if he's in the project
    create : (add)
        A client cannot add a member to a project
        A member can add a client (not a member) to a project
        An admin can add everyone
    update : None
    delete :
        A client cannot remove a member of a project
        A member can remove only a client of a project
        An admin can remvoe everyone
    """

    def __init__(self):
        self.form_listing = ProjectMemberListing
        self.form = ProjectMemberForm
        self.model = ProjectMember

    def check_write_access(self, **kwargs):
        if g.member.status == 'CLIENT':
            return False

    def check_write_authorizations(self, member):
        # We already checked if status == 'CLIENT'
        if not g.member.admin:
            if not member.status == 'CLIENT':
                return abort(403)

    def pre_create(self, form, **kwargs):
        return self.check_write_authorizations(form.member_id.member) # Shall have been populated

    def post_create(self, form, instance, project_id):
        # Check that member_id exists in this project
        # Check that application_plan_id also !
        # Check that project_id also
        instance.project_id = project_id
        instance.application_id = g.application.id

    def pre_delete(self, instance, project_id, id):
        return self.check_write_authorizations(instance.member)


project_members = Blueprint('project_members', __name__)
ProjectMemberAPI.register(project_members, '/<int:project_id>/members/', actions=['list', 'details', 'create', 'delete'])

app = (projects, project_members)
