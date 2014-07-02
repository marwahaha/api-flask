# coding:utf-8

from database import db
from utils.models import RemovableModel
from sqlalchemy.orm import relationship, backref

import datetime

class File(db.Model, RemovableModel):
    __tablename__ = 'project_files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed = db.Column(db.DateTime, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    author = relationship('Member', backref=backref('project_files'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', backref=backref('project_files'))

    def __repr__(self):
        return self.name
