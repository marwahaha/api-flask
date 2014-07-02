# coding:utf-8

from tests import BaseTestCase
import json

class TestCreate(BaseTestCase):
    __display__ = "Members > Create (client)"

    def setUp(self):
    	self.mode = 'client'

        self.data = {
            'display': 'Hello', # Testing no display
            'email': 'admin@example.com', # Testing invalid email
            'password': 'hallo',
            'confirm': 'hallo', # Testing mismatch
            'website': 'http://www.reflectiv.net', # testing invalid url
            'lang': 'en', # Testing 1, 3 chars, no chars
            'owner_id': None, # Testing with existing, none, not exists
            'status': 'CLIENT', # testing with MEMBER, MEMBER with limitation rights, invalid status
        }

    def test_create_generic_client(self):
        """Test creating a client"""
        self.data['email'] = 'client@example.com'
        result = self.post("/v1/members/", data=self.data)
        self.assertEqual(result.status_code, 403)