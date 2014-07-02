# coding:utf-8

from database import db
from sqlalchemy.orm import relationship, backref

import datetime

class Message(db.Model):
    __tablename__ = 'project_messages'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    author = relationship('Member', backref=backref('project_messages'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', backref=backref('project_messages'))

    def __repr__(self):
        return self.message
