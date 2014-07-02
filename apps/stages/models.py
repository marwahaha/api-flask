# coding:utf-8

from database import db
from utils.models import RemovableModel

from sqlalchemy.orm import relationship, backref

import datetime

class Stage(db.Model, RemovableModel):
    __tablename__ = 'stages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    sort = db.Column(db.SmallInteger, nullable=True)
    removed = db.Column(db.DateTime, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    author = relationship('Member', backref=backref('stages'))

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('stages'))

    def __repr__(self):
        return self.name


class ProjectStage(db.Model):
    __tablename__ = 'project_stages'

    id = db.Column(db.Integer, primary_key=True)

    started = db.Column(db.DateTime, nullable=False)
    ended = db.Column(db.DateTime, nullable=False)

    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'), nullable=False)
    stage = relationship('Stage', backref=backref('project_stages'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', backref=backref('project_stages'))
