# coding:utf-8

from werkzeug.utils import import_string

from unittest import TestCase
import os, unittest, config

import json

class BlueprintTesting():
    def suite(self):
        # Must return a suite of objects
        suite = unittest.TestSuite()

        for blueprint in config.Testing.BLUEPRINTS:
            if isinstance(blueprint, basestring):
                package = blueprint
            else:
                package = blueprint[0]

            self._fetch_directory('apps/%s/tests' % package, suite)

        return suite

    def _fetch_directory(self, directory, suite):
        """
        Fetching for test files recursively
        """
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                new_path = '%s/%s' % (directory, file)
                if os.path.isdir(new_path):
                    self._fetch_directory(new_path, suite)

                if not file.startswith('__init__') and file.endswith('.py'):
                    self._load_suite(new_path, suite)

    def _load_suite(self, file, suite):
        # We remove the "apps." at first, and then the ".py" ending
        package = file.replace('/', '.')[5:-3]
        module = import_string(package)
        suite.addTest(unittest.findTestCases(module))

class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        print ""
        print cls.__display__

        from main import app_factory
        from database import db, create_all, drop_all

        cls.app = app_factory(config.Testing)
        cls.client = cls.app.test_client()

        cls.app_key = 'testing'
        cls.api_token_admin = 'adminadmin'
        cls.api_token_member = 'membermember'
        cls.api_token_client = 'clientclient'

        drop_all()
        create_all()

        db.engine.execute('INSERT INTO `applications` (id, name, display, app_key, status) VALUES (1, "reflectiv", "Reflectiv", "testing", "DEV");')
        db.engine.execute('INSERT INTO `application_plans` (id, display, description, application_id, sms, members, storage, projects, monthly_price, yearly_price, currency, share) VALUES (1, "Free membership", "Free membership", 1, 0, 3, 0, 3, 0, 0, "USD", 50);')

        db.engine.execute('INSERT INTO `organizations` (name, display, currency, application_id, application_plan_id, created) VALUES ("reflectiv", "Reflectiv", "USD", 1, 1, "2014-04-01 00:00:00");')

        db.engine.execute('INSERT INTO `members` (id, display, organization_id, status, is_admin, is_disabled, lang) VALUES (1, "Administrator", 1, "MEMBER", 1, 0, "en"), (2, "Simple Member", 1, "MEMBER", 0, 0, "en"), (3, "Client", 1, "CLIENT", 0, 0, "en");')

        db.engine.execute('INSERT INTO `sessions` (expires, token, member_id) VALUES ("2015-12-31 00:00:00", "adminadmin", 1), ("2015-12-31 00:00:00", "membermember", 2), ("2015-12-31 00:00:00", "clientclient", 3);')


    @classmethod
    def tearDownClass(cls):
        from database import db, drop_all, remove_session

        drop_all()
        remove_session()


    def setUp(self):
        self.mode = 'admin'

    def tearDown(self):
        pass

    def get_params(self):
        return {
            'headers': {
                'app-key': self.app_key,
                'api-token': getattr(self, 'api_token_%s' % self.mode)
            }
        }

    def get(self, url):
        return self.client.get(url, **self.get_params())

    def post(self, url, data=None):
        return self.client.post(url, data=data, **self.get_params())

    def put(self, url, data=None):
        return self.client.put(url, data=data, **self.get_params())

    def delete(self, url):
        return self.client.delete(url, **self.get_params())
