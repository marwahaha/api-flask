# coding:utf-8

from flask import g
from database import db
from utils.models import RemovableModel, SeenModel, JsonSerializable, ModelForm

from sqlalchemy.orm import relationship, backref

import datetime

class Project(db.Model, ModelForm, SeenModel, JsonSerializable, RemovableModel):
    __tablename__ = 'projects'
    __jsonserialize__ = ['id', 'display', 'description', 'website', 'start', 'due', 'seen', 'last_seen', 'created', 'modified', 'removed', ('get_invoices', 'invoices')]

    id = db.Column(db.Integer, primary_key=True)
    display = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(250), nullable=True)

    start = db.Column(db.DateTime, nullable=True)
    due = db.Column(db.DateTime, nullable=True)
    
    removed = db.Column(db.DateTime, nullable=True)

    seen = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=None)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=None)

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('projects'))

    stages = relationship('ProjectStage', backref=backref('projects'))
    messages = relationship('Message', backref=backref('projects'))
    notes = relationship('Note', backref=backref('projects'))
    files = relationship('File', backref=backref('projects'))

    # invoices

    def __repr__(self):
        return self.display

    def get_invoices(self):
        if not self.invoices:
            return []

        invoices = []
        for invoice in self.invoices:
            invoices.append({
                'id': invoice.id,
                'display': invoice.reference,
                'reference': invoice.reference,
                'total': invoice.get_total(),
                'status': invoice.get_status(),
                'currency': invoice.currency
            })

        return invoices


    @classmethod
    def find_by_id(cls, id):
        """
        Return the member of id member_id if exists in this application
        """
        query = cls.query.filter(cls.id == id).filter(cls.organization_id == g.organization.id)

        if g.member.admin:
            return query.first()

        project_ids = []
        for project_member in g.member.projects:
            project_ids.append(project_member.project_id)

        return query.joinfilter(cls.id.in_(project_ids)).first()

    @classmethod
    def find(cls, form):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.organization_id == g.organization.id)

        if not g.member.admin:
            # Assuring that the asking user as the rights to see this user
            project_ids = []
            for project_member in g.member.projects:
                project_ids.append(project_member.project_id)

            query = query.filter(Project.id.in_(project_ids))

        return cls.paginate(query, form)

    @classmethod
    def filter_by_member_id(cls, query, field):
        query = query.join(ProjectMember).filter(ProjectMember.member_id == field.data)

        return query

    @classmethod
    def count_projects(cls):
        return cls.query.filter(cls.organization_id == g.organization.id).count()




member_statuses = ('CLIENT', 'MEMBER')

class ProjectMember(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'project_members'
    __jsonserialize__ = ['id', 'member', 'project']

    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    member = relationship('Member', backref=backref('projects'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', backref=backref('members'))

    def __serialize__(self):
        return self.to_json()

    @classmethod
    def find_by_id(cls, project_id, id):
        query= cls.query.join(Project) \
                        .filter(Project.application_id == g.application.id) \
                        .filter(cls.project_id == project_id) \
                        .filter(cls.member_id == id) \


        if not g.member.admin:
            is_in_project = False
            for project in g.member.projects:
                if project.id == project_id:
                    is_in_project = True
                    break

            if not is_in_project:
                return None

        return query.fist()

    @classmethod
    def find(cls, form, project_id):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.project_id == project_id).join(Project).filter(Project.application_id == g.application.id)

        if not g.member.admin:
            is_in_project = False
            for project in g.member.projects:
                if project.id == project_id:
                    is_in_project = True
                    break

            if not is_in_project:
                # Dummy query to return no values
                # Because this user is not allowed to list members of the project
                query = query.filter(cls.project_id == 0)

        return cls.paginate(query, form)

    @classmethod
    def order_by_member(cls, query, order="asc"):
        from members.models import Member
        return query.join(cls.member, aliased=True).order_by(getattr(Member.display, order.lower())())
