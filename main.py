# -*- coding:utf-8 -*-

import os
import sys

import logging
from logging.handlers import SMTPHandler
from logging import Formatter

from flask import Flask, render_template, make_response, request, jsonify, redirect, g
from werkzeug import import_string

from utils.mails import TlsSMTPHandler



# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))


def __import_variable(blueprint_path, module, variable_name):
    path = '.'.join(blueprint_path.split('.') + [module])
    mod = __import__(path, fromlist=[variable_name])
    return getattr(mod, variable_name)


def config_str_to_obj(cfg):
    if isinstance(cfg, basestring):
        module = __import__('config', fromlist=[cfg])
        return getattr(module, cfg)
    return cfg


def app_factory(config, app_name=None, blueprints=None):
    app_name = app_name or __name__
    app = Flask(app_name)

    config = config_str_to_obj(config)
    configure_app(app, config)
    configure_logger(app, config)
    configure_blueprints(app, blueprints or config.BLUEPRINTS)
    configure_error_handlers(app)
    configure_database(app)
    configure_extensions(app)
    configure_template_filters(app)
    configure_before_after_request(app)
    configure_views(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)
    app.config.from_envvar("APP_CONFIG", silent=True)  # available in the server


def configure_logger(app, config):
    log_filename = config.LOG_FILENAME

    if not app.debug:
        # Create a file logger since we got a logdir
        log_file = logging.FileHandler(filename=log_filename)
        formatter = logging.Formatter(config.LOG_FORMAT)
        log_file.setFormatter(formatter)
        log_file.setLevel(config.LOG_LEVEL)
        app.logger.addHandler(log_file)

        mail_handler = TlsSMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']), 'errors@2lead.in', ['admin@2lead.in',], '[2lead.in] - An exception occured.', (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(Formatter('''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s

            Message:

            %(message)s
            '''))
        app.logger.addHandler(mail_handler)

    app.logger.info("Logger started")


def configure_blueprints(app, blueprints):
    """Registers all blueprints set up in config.py"""
    for blueprint_config in blueprints:
        blueprint, kw = None, {}

        if isinstance(blueprint_config, basestring):
            blueprint = blueprint_config
        elif isinstance(blueprint_config, tuple):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]
        else:
            print "Error in BLUEPRINTS setup in config.py"
            print "Please, verify if each blueprint setup is either a string or a tuple."
            exit(1)

        blueprint = __import_variable(blueprint, 'views', 'app')
        if isinstance(blueprint, tuple):
            for bp in blueprint:
                app.register_blueprint(bp, **kw)
        else:
            app.register_blueprint(blueprint, **kw)


def configure_error_handlers(app):
    # We ignore error handlers in case of dev mode
    if app.debug:
        return

    @app.errorhandler(401)
    def page_not_found(e):
        return jsonify({'error': 'Authorization required.', 'code': 401}), 401

    @app.errorhandler(403)
    def page_not_found(e):
        return jsonify({'error': 'Access Forbidden.', 'code': 403}), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Page not found.', 'code': 404}), 404

    @app.errorhandler(405)
    def page_not_found(e):
        return jsonify({'error': 'Method not allowed.', 'code': 405}), 405

    @app.errorhandler(410)
    def internal_server_error(e):
        return jsonify({'error': 'Gone.', 'code': 410}), 410

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_server_error(e):
        print e
        return jsonify({'error': 'Internal server error.', 'code': 500}), 500

def configure_database(app):
    """
    Database configuration should be set here
    """
    # uncomment for sqlalchemy support
    from database import db
    db.app = app
    db.init_app(app)

def configure_template_filters(app):
    """Configure filters and tags for jinja"""

    """
    app.jinja_env.filters['timesince'] = import_string('utils.filters.timesince')
    app.jinja_env.filters['timeuntil'] = import_string('utils.filters.timeuntil')

    app.jinja_env.filters['datetimeformat'] = import_string('flask.ext.babel.format_datetime')
    app.jinja_env.filters['dateformat'] = import_string('flask.ext.babel.format_date')
    app.jinja_env.filters['timeformat'] = import_string('flask.ext.babel.format_time')

    app.jinja_env.globals['incident_url'] = import_string('utils.functions.incident_url')
    """

    app.jinja_env.filters['dateformat'] = import_string('utils.template.dateformat')
    app.jinja_env.filters['nl2br'] = import_string('utils.template.nl2br')
    app.jinja_env.filters['money'] = import_string('utils.template.money')


def configure_extensions(app):
    """Configure extensions like mail and login here"""
    from utils.middleware import HTTPMethodOverrideMiddleware
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)


def configure_before_after_request(app):
    @app.after_request
    def after_request_cors(data):
        """ Implementing CORS """
        response = make_response(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Host, App-Key, Auth-Token, Organization'

        return response


def configure_views(app):
    """Add some simple views here like index_view"""

    @app.route("/")
    def index_view():
        return redirect('/v1/', 301)

    @app.route("/v1/")
    def documentation_v1():
        return render_template("v1/documentation.html")

    #for rule in app.url_map.iter_rules():
    #    print rule
