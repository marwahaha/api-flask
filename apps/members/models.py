# coding:utf-8

from flask import g
from database import db
from utils.models import ModelForm, SeenModel, RemovableModel, JsonSerializable
from projects.models import Project, ProjectMember, member_statuses

from sqlalchemy.orm import relationship, backref

import datetime
import bcrypt
import hashlib

class Profile(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'profiles'
    __table_args__ = (
        db.UniqueConstraint('email', 'application_id'),
    )

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(100), nullable=True)

    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    application = relationship('Application', backref=backref('profiles'))

    def __repr__(self):
        return self.email

    def set_password(self, clear):
        self.password = bcrypt.hashpw(clear, bcrypt.gensalt())

    def check_passwd(self, password):
        return (bcrypt.hashpw(password, self.password) == self.password)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter(cls.email == email) \
                .filter(cls.application_id == g.application.id) \
                .first()

    def __jsonserialize__(self):
        organizations = []
        for account in self.accounts:
            organizations.append({
                'name': account.organization.name,
                'display': account.organization.display,
                'status': account.status,
                'admin': account.admin
            })

        return {
            'email': self.email,
            'organizations': organizations
        }

    @classmethod
    def is_email_available(cls, email, id=None):
        if id:
            return cls.query.filter(cls.email == email) \
                .filter(cls.application_id == g.application.id) \
                .filter(cls.id != id) \
                .first() == None
        else:
            return cls.query.filter(cls.email == email) \
                .filter(cls.application_id == g.application.id) \
                .first() == None


class Member(db.Model, ModelForm, SeenModel, RemovableModel, JsonSerializable):
    __tablename__ = 'members'


    __jsonserialize__ = ['id', 'display', ('get_email', 'email'), ('get_email_md5', 'email_md5'), 'address',
                         'office', 'mobile', 'fax', 'website', 'description', 'business_number',
                         'sector', 'seen', 'last_seen', 'created', 'modified', 'lang',
                         'removed', 'owner', 'projects', 'status', 'admin']

    id = db.Column(db.Integer, primary_key=True)
    display = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    address = db.Column(db.Text(250), nullable=True)

    office = db.Column(db.String(250), nullable=True)
    mobile = db.Column(db.String(250), nullable=True)
    fax = db.Column(db.String(250), nullable=True)

    website = db.Column(db.String(250), nullable=True)

    description = db.Column(db.Text, nullable=True)

    sector = db.Column(db.String(250), nullable=True)

    seen = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=None)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=None)

    lang = db.Column(db.String(2), nullable=False, default="en")

    business_number = db.Column(db.String(250), nullable=True)

    disabled = db.Column('is_disabled', db.Boolean, nullable=False, default=False)
    removed = db.Column(db.DateTime)

    owner_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    owner = relationship('Member', backref=backref('clients'), remote_side=[id])

    #comments = relationship('MemberComment', backref=backref('members'), foreign_keys="MemberComment.client_id")

    status = db.Column(db.Enum(*member_statuses))
    admin = db.Column('is_admin', db.Boolean, nullable=False, default=False) # Super admin here

    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
    profile = relationship('Profile', backref=backref('accounts'))

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('members'))

    def __repr__(self):
        return self.display

    def get_email(self):
        return self.email or self.profile.email

    def get_email_md5(self):
        return hashlib.md5(self.profile.email).hexdigest()

    @classmethod
    def find_by_id(cls, id):
        """
        Return the member of id member_id if exists in this application
        """
        query = cls.query.filter(cls.id == id).filter(cls.organization_id == g.organization.id)

        if g.member.status != 'CLIENT':
            return query.first()

        # Assuring that the asking user as the rights to see this user
        project_ids = []
        for project_member in g.member.projects:
            project_ids.append(project_member.project_id)

        if len(project_ids) > 0:
            query = query.join(ProjectMember).filter(
                    ProjectMember.member_id.in_(
                        ProjectMember.query.filter(
                            ProjectMember.id.in_(project_ids)
                        )
                    )
                )
        else:
            query = query.filter(1 == 2)

        return query.first()


    @classmethod
    def find(cls, form):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.organization_id == g.organization.id)

        if g.member.status == 'CLIENT':
            project_ids = []
            for project_member in g.member.projects:
                project_ids.append(project_member.project_id)

            if len(project_ids) > 0:
                query = query.join(ProjectMember).filter(
                        ProjectMember.member_id.in_(
                            ProjectMember.query.filter(
                                ProjectMember.id.in_(project_ids)
                            )
                        )
                    )
            else:
                query = query.filter(1 == 2)

        return cls.paginate(query, form)


    @classmethod
    def count_members(cls):
        return cls.query.filter(cls.organization_id == g.organization.id).count()

    @classmethod
    def filter_by_project_id(cls, query, field):
        query = query.join(ProjectMember).filter(ProjectMember.project_id == field.data)

        return query

    @classmethod
    def filter_by_email(cls, query, field):
        query = query.join(Profile).filter(Profile.email.ilike(field.data + '%'))

        return query

    @classmethod
    def order_by_owner(cls, query, order="asc"):
        return query.join(cls.owner, aliased=True).order_by(getattr(cls.display, order.lower())())

    @classmethod
    def display_from_email(self, email):
        return email[0:email.index('@')].replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', ' ')


    @classmethod
    def is_email_available(cls, email, id=None):
        if id:
            return cls.query.filter(cls.email == email) \
                .filter(cls.organization_id == g.organization.id) \
                .filter(cls.id != id) \
                .first() == None
        else:
            return cls.query.filter(cls.email == email) \
                .filter(cls.organization_id == g.organization.id) \
                .first() == None

class MemberComment(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'member_comments'
    __jsonserialize__ = ['id', 'message', 'author', 'client', 'created']

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.Text, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    author = relationship('Member', backref=backref('author_comments'), foreign_keys=[author_id])

    client_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    client = relationship('Member', backref=backref('comments'), foreign_keys=[client_id])

    def __repr__(self):
        if len(self.message) > 25:
            return '{0}...'.format(self.message[0:25], )

        return self.message

    @classmethod
    def find_by_id(cls, id, member_id=None, author_id=None):
        """
        Return the member of id member_id if exists in this application
        """
        query = cls.query.filter(cls.id == id)
        if member_id:
            query = query.filter(cls.client_id == member_id)

        if author_id:
            query = query.filter(cls.author_id == author_id)

        return query.first()

    @classmethod
    def find(cls, form, member_id=None, author_id=None):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)

        if member_id:
            query = query.filter(cls.client_id == member_id)
        if author_id:
            query = query.filter(cls.author_id == author_id)

        return cls.paginate(query, form)
