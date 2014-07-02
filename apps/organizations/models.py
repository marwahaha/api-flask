# coding:utf-8

from flask import g
from database import db
from utils.models import RemovableModel, JsonSerializable, ModelForm

from sqlalchemy.orm import relationship, backref

import json

import datetime

class Organization(db.Model, ModelForm, JsonSerializable, RemovableModel):
    __tablename__ = 'organizations'
    __table_args__ = (
        db.UniqueConstraint('name', 'application_id'),
    )

    __jsonserialize__ = ['id', 'display', 'name', 'description', 'address', 'website', 'business_number', 'logo_url', 'currency',
                            ('get_defaults', 'defaults'), 'created', 'removed', 'application_plan_id', 'show_payments']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    display = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(250), nullable=True)
    business_number = db.Column(db.String(250), nullable=True)

    logo = db.Column(db.String(250), nullable=True)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed = db.Column(db.DateTime, nullable=True)

    currency = db.Column(db.String(3), nullable=False, default="USD")

    defaults = db.Column(db.Text, nullable=True)

    show_payments = db.Column('is_show_payments', db.Boolean, nullable=False, default=True)

    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    application = relationship('Application', backref=backref('organizations'))

    application_plan_id = db.Column(db.Integer, db.ForeignKey('application_plans.id'), nullable=False)
    application_plan = relationship('ApplicationPlan')

    def __repr__(self):
        return self.display

    def logo_url(self):
        return self.logo

    def get_defaults(self):
        return json.loads(self.defaults);

    @classmethod
    def find_by_name(cls, name):
        if g.organization.name != name:
            return None
        return cls.query.filter(cls.name == name).filter(cls.application_id == g.application.id).first()

    @classmethod
    def find(cls, form):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.application_id == g.application.id)

        return cls.paginate(query, form)

    @classmethod
    def filter_by_member_id(cls, query, field):
        query = query.join(ProjectMember).filter(ProjectMember.member_id == field.data)

        return query
