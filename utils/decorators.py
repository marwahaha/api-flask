# coding=utf-8

from functools import wraps
from flask import request, jsonify, g, abort

from auth.models import Session
import datetime

def url_access(view_func):
    def _decorator(*args, **kwargs):
        from members.models import Member
        from organizations.models import Organization

        session = Session.find_by_access(request.args.get('key'))

        if not session:
            return 'Session has expired.', 401

        if not request.args.get('organization'):
            return 'Organization is required.', 401

        member = Member.query.filter(Member.profile_id == session.profile_id) \
                              .join(Member.organization) \
                              .filter(Organization.name == request.args.get('organization')) \
                              .first()

        if not member:
            return abort(404)

        g.member = member
        g.organization = member.organization
        g.application = member.organization.application

        return view_func(*args, **kwargs)

    return wraps(view_func)(_decorator)


def authenticated(view_func):
    def _decorator(*args, **kwargs):
        from members.models import Member
        from organizations.models import Organization

        if 'app-key' not in request.headers:
            response = jsonify({'code': 401, 'message': 'App-Key header is required.'})
            response.status_code = 401
            return response

        if 'auth-token' not in request.headers:
            response = jsonify({'code': 401, 'message': 'Auth-Token header is required.'})
            response.status_code = 401
            return response

        if 'organization' not in request.headers:
            response = jsonify({'code': 401, 'message': 'Organization header is required.'})
            response.status_code = 401
            return response

        session = Session.find_by_token(request.headers['auth-token'])

        if not session or session.profile.application.app_key != request.headers['app-key']:
            response = jsonify({'code': 401, 'message': 'Session has expired.'})
            response.status_code = 401
            return response

        member = Member.query.filter(Member.profile_id == session.profile_id) \
                              .join(Member.organization) \
                              .filter(Organization.name == request.headers['organization']) \
                              .first()

        if not member:
            response = jsonify({'code': 401, 'message': 'Organization not found.'})
            response.status_code = 401
            return response

        g.member = member
        g.organization = member.organization
        g.application = member.organization.application

        return view_func(*args, **kwargs)

    return wraps(view_func)(_decorator)
