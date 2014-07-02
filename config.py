# -*- config:utf-8 -*-

import logging
from datetime import timedelta
import os

project_name = "2leadin"


class Config(object):
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))
    # use DEBUG mode?
    DEBUG = False

    # use TESTING mode?
    TESTING = False

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@127.0.0.1/2leadin?charset=utf8"
    SQLALCHEMY_ECHO = False

    CSRF_ENABLED = False
    SECRET_KEY = "\x8f\x85Gm\xe6\xdd\xfd\xfb)D\x05+\x92\xc9F\xd9\x0b\x0b\xc5>\x9b\xd5\xa1^"  # import os; os.urandom(24)

    # LOGGING
    LOGGER_NAME = "%s_log" % project_name
    LOG_FILENAME = "%s.log" % project_name
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s" # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # EMAIL CONFIGURATION
    MAIL_SERVER = "127.0.0.1"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

    # WTForm configuration
    WTF_CSRF_ENABLED=False

    # Amazon
    AWS_ACCESS_KEY = 'amazon_key'
    AWS_SECRET_KEY = 'amazon_secret'

    # see example/ for reference
    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [
        ('base'),
        ('organizations', {'url_prefix': '/v1/organizations'}),
        ('auth',          {'url_prefix': '/v1/auth'}),
        ('activities',    {'url_prefix': '/v1/activities'}),
        ('accounts',      {'url_prefix': '/v1/account'}),     # Special path for managing connected members
        ('members',       {'url_prefix': '/v1/members'}),
        ('projects',      {'url_prefix': '/v1/projects'}),
        ('files',         {'url_prefix': '/v1/files'}),
        ('invoices',      {'url_prefix': '/v1/invoices'}),
        ('messages',      {'url_prefix': '/v1/messages'}),
        ('notes',         {'url_prefix': '/v1/notes'}),
        ('stages',        {'url_prefix': '/v1/stages'}),
        ('tasks',         {'url_prefix': '/v1/tasks'})
    ]


class Dev(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@127.0.0.1/2leadin_dev?charset=utf8"
    DEBUG = True
    MAIL_DEBUG = False
    SQLALCHEMY_ECHO = False

    # EMAIL CONFIGURATION
    MAIL_SERVER = "127.0.0.1"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

class Prod(Config):
    pass


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/2leadin_test.sqlite"
    SQLALCHEMY_ECHO = False
