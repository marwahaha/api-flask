# coding:utf-8

from database import db
from utils.models import RemovableModel

from sqlalchemy.orm import relationship, backref

import datetime

class Task(db.Model, RemovableModel):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    due = db.Column(db.DateTime, nullable=True)

    important = db.Column('is_important', db.Boolean, nullable=False, default=False)
    done = db.Column('is_done', db.Boolean, nullable=False, default=False)

    removed = db.Column(db.DateTime, nullable=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    owner = relationship('Member', backref=backref('tasks'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    project = relationship('Project', backref=backref('tasks'))

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('tasks'))

    notifications = relationship('TaskNotification', backref=backref('tasks'))


notification_types = ('EMAIL', 'SMS')

class TaskNotification(db.Model):
    __tablename__ = 'task_notifications'

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = relationship('Task')

    type = db.Column(db.Enum(*notification_types))
    time_before = db.Column(db.SmallInteger, nullable=False) # In minutes
