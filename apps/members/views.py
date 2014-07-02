# coding:utf-8

from flask import Blueprint, g, abort, jsonify, request
from utils.api import BaseAPI, FormApiError
from utils.decorators import authenticated

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from .forms import *
from .models import *

import datetime

class MemberAPI(BaseAPI):
    def __init__(self):
        self.form_listing = MemberListing
        self.form = MemberForm
        self.model = Member

    def get_form_as_dict(self, form, **kwargs):
        data = form.get_as_dict()
        del data['confirm']
        del data['password']

        return data

    def pre_create(self, form):
        """
        A client cannot create a member
        A Member can create only a client
        An admin can create everything, if authorize from his application_plan
        """
        if g.member.status == 'CLIENT':
            return abort(403)

        if g.member.status == 'MEMBER':
            if form.status.data == 'MEMBER':
                if g.member.admin:
                    members = Member.count_members()
                    if g.organization.application_plan.members <= members:
                        return abort(402)
                else:
                    return abort(403)

        if not Member.is_email_available(form.email.data):
            raise FormApiError('author_id', 'This email is already taken.')

        if not form.lang.data:
            form.lang.data = g.member.lang

    def pre_update(self, form, instance, id):
        """
        A client can update his profile, and only his
        A member can edit every clients profile, and his
        An admin can edit everyone's profile
        """
        if g.member.status == 'CLIENT' and g.member.id != id:
            return abort(403)

        if g.member.status == 'MEMBER':
            if not g.member.admin:
                if form.status.data == 'MEMBER' and g.member.id != id:
                    return abort(403)

        if not Member.is_email_available(form.email.data):
            raise FormApiError('author_id', 'This email is already taken.')

    def post_create(self, form, instance):
        if not instance.owner_id:
            instance.owner_id = g.member.id

        instance.organization_id = g.organization.id
        instance.created = datetime.datetime.utcnow()

        profile = Profile.find_by_email(instance.email)
        if not profile:
            profile = Profile()
            profile.email = instance.email
            profile.application_id = g.application.id
            profile.save()

        instance.profile_id = profile.id

    def post_update(self, form, instance):
        profile = Profile.find_by_email(form.email.data)
        if not profile:
            instance.profile.email = form.email.data
            instance.profile.save()


    def pre_delete(self, instance, id):
        """
        A client cannot delete
        A Member can only delete a client
        An admin can delete everyone
        """
        if g.member.status == 'CLIENT':
            return abort(403)

        if not g.member.admin:
            if instance.status == 'MEMBER':
                return abort(403)

    def post_delete(self, instance, id):
        from invoices.models import Invoice
        Invoice.query.filter(Invoice.client_id == instance.id).update({'client_id': None})



members = Blueprint('members', __name__)
MemberAPI.register(members, '/')

@members.route('/sectors/')
def list_sectors():
    if not request.args.get('key'):
        return abort(400)

    db = SQLAlchemy()

    key = request.args.get('key') + '%'

    result = []
    rows = db.engine.execute(text("SELECT sector FROM `members` WHERE IFNULL(sector, '') != '' AND sector LIKE :key GROUP BY sector LIMIT 10;"), key=key)
    for row in rows:
        result.append({'id': row['sector'], 'text': row['sector']})

    return jsonify({'items': result}), 200

class MemberCommentAPI(BaseAPI):
    def __init__(self):
        self.form_listing = MemberCommentListing
        self.form = MemberCommentForm
        self.model = MemberComment

    """
    Only Members can access comments
    """
    def check_read_access(self, type, **kwargs):
        if g.member.status == 'CLIENT':
            return False

    def check_write_access(self, type, **kwargs):
        if g.member.status == 'CLIENT':
            return False


    def pre_create(self, form, member_id):
        if member_id == g.member.id:
            raise FormApiError('author_id', 'You can not comment on yourself.')

    def pre_update(self, form, instance, member_id, id):
        if member_id == g.member.id:
            raise FormApiError('author_id', 'You can not comment on yourself.')

        if g.member.admin or instance.author_id == g.member.id:
            return None
        else:
            return abort(403)

    def pre_delete(self, instance, member_id, id):
        if g.member.admin or instance.author_id == g.member.id:
            return None
        else:
            return abort(403)

    def post_create(self, form, instance, member_id):
        instance.author_id = g.member.id
        instance.client_id = member_id


comments = Blueprint('members_comments', __name__)
MemberCommentAPI.register(comments, '/<int:member_id>/comments/')


class MemberAuthorCommentAPI(BaseAPI):
    def __init__(self):
        self.form_listing = MemberCommentListing
        self.model = MemberComment

    """
    Only Members can access comments
    """
    def check_read_access(self, type, **kwargs):
        if g.member.status == 'CLIENT':
            return abort(403)


author_comments = Blueprint('members_author_comments', __name__)
MemberAuthorCommentAPI.register(author_comments, '/<int:author_id>/author-comments/', actions=['list', 'details'])

app = (members, comments, author_comments)
