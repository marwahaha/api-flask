# coding:utf-8

from flask import g
from database import db
from utils.models import RemovableModel
from sqlalchemy.orm import relationship, backref

import datetime

# TODO : missing tables :
# history, history_fields, login_token, reseller?

application_statuses = ('DEV', 'PROD')

class Application(db.Model, RemovableModel):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    display = db.Column(db.String(50), nullable=False)

    name = db.Column(db.String(50), nullable=False, unique=True)
    app_key = db.Column(db.String(50), nullable=False, unique=True)

    website = db.Column(db.String(250), nullable=True)

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    removed = db.Column(db.DateTime)

    status = db.Column(db.Enum(*application_statuses))

    plans = relationship('ApplicationPlan', backref=backref('applications'))

    @classmethod
    def find_by_key(cls, key):
        return cls.query \
                .filter(cls.app_key == key) \
                .filter((cls.removed == None) | (cls.removed < datetime.datetime.utcnow())) \
                .first()


class ApplicationPlan(db.Model, RemovableModel):
    __tablename__ = 'application_plans'

    id = db.Column(db.Integer, primary_key=True)
    display = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    application = relationship('Application')

    sms = db.Column(db.Integer, default=0, nullable=False)           # How many SMS per members this application accepts
    members = db.Column(db.Integer, default=0, nullable=False)       # How many members this option accept
    storage = db.Column(db.Integer, default=0, nullable=False)       # In Mb
    projects = db.Column(db.Integer, default=0, nullable=False)      # Number of projects allowed
    monthly_price = db.Column(db.Integer, nullable=False)            # Price per months, in cents, to pay for this option
    yearly_price = db.Column(db.Integer, nullable = False)           # Price per years, in cents, to pay for this option
    currency = db.Column(db.String(4), nullable=False, default="USD")
    share = db.Column(db.Integer)                                    # Amount taken by 2Lead.in, The partner will get monthly_price - share

    start = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    removed = db.Column(db.DateTime)

    @classmethod
    def find_by_id(cls, id):
        return cls.query \
            .filter(cls.id == id) \
            .filter(cls.application_id == g.application.id) \
            .filter((cls.removed == None) | (cls.removed < datetime.datetime.utcnow())) \
            .first()

