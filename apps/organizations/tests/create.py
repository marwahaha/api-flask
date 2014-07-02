# coding:utf-8

from tests import BaseTestCase
import json

class TestCreate(BaseTestCase):
    __display__ = "Organizations > Create"

    def test_create_correct(self):
        """Creating a new organization by respecting the form"""

        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'application_plan_id': 1,
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 201)

    def test_create_empty_display(self):
        data = {
            'name': 'TwoLeadIn',
            'application_plan_id': 10,
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('display' in json_result)

    def test_create_invalid_plan_id(self):
        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'application_plan_id': 10,
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('application_plan_id' in json_result)

    def test_create_empty_plan_id(self):
        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('application_plan_id' in json_result)

    def test_create_empty_name(self):
        data = {
            'application_plan_id': 1,
            'display': '2Lead.in',
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('name' in json_result)

    def test_create_invalid_email(self):
        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'application_plan_id': 1,
            'member_email': 'adminexample.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('member_email' in json_result)

    def test_create_password_mismatch(self):
        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'application_plan_id': 1,
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cx2cx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 400)

        json_result = json.loads(result.data)
        self.assertTrue('member_password' in json_result)


    def test_create_invalid_app_key(self):
        self.app_key = "kikoo"
        data = {
            'name': 'TwoLeadIn',
            'display': '2Lead.in',
            'application_plan_id': 1,
            'member_email': 'admin@example.com',
            'member_password': 'cxcx',
            'member_confirm': 'cxcx'
        }

        result = self.post("/v1/organizations/", data=data)
        self.assertEqual(result.status_code, 401)

        json_result = json.loads(result.data)
        self.assertTrue('message' in json_result)
        self.assertTrue('code' in json_result)
        self.assertEqual(json_result['code'], 401)
