# coding:utf-8

from database import db
from sqlalchemy.orm import relationship, backref

from utils.models import JsonSerializable, ModelForm

import datetime
import uuid

class Session(db.Model, JsonSerializable, ModelForm):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)

    expires = db.Column(db.DateTime)
    token = db.Column(db.String(100), nullable=False, unique=True)
    access = db.Column(db.String(100), nullable=False, unique=True)

    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    profile = relationship('Profile', backref=backref('sessions'))

    def __repr__(self):
        return self.token

    def __jsonserialize__(self):
        organizations = []
        for account in self.profile.accounts:
            organizations.append({
                'name': account.organization.name,
                'display': account.organization.display,
                'status': account.status,
                'admin': account.admin
            })

        return {
            'token': self.token,
            'access': self.access,
            'expires': self.expires,
            'organizations': organizations
        }

    def __init__(self, profile_id):
        self.delete_old(profile_id)

        self.profile_id = profile_id
        self.refresh_expires()
        self.token = str(uuid.uuid4()).replace('-', '')
        self.access = str(uuid.uuid4()).replace('-', '')

    def refresh_expires(self):
        self.expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)

    @classmethod
    def delete_old(cls, profile_id):
        return cls.query.filter(cls.profile_id == profile_id).delete()

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter(cls.expires > datetime.datetime.utcnow()).filter(cls.token == token).first()

    @classmethod
    def find_by_access(cls, access):
        return cls.query.filter(cls.expires > datetime.datetime.utcnow()).filter(cls.access == access).first()
