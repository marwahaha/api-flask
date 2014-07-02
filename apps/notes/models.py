# coding:utf-8

from database import db
from utils.models import RemovableModel

from sqlalchemy.orm import relationship, backref

import datetime

class Note(db.Model, RemovableModel):
    __tablename__ = 'project_notes'

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed = db.Column(db.DateTime, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    author = relationship('Member', backref=backref('project_notes'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', backref=backref('project_notes'))

    def __repr__(self):
        return self.note
