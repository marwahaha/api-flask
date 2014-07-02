# coding:utf-8

from tests import BaseTestCase
import json

class TestCreate(BaseTestCase):
    __display__ = "Members > Create (admin)"

    def setUp(self):
    	self.mode = 'admin'
    	
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

    def test_create_generic_admin(self):
        """Test creating a client"""
        result = self.post("/v1/members/", data=self.data)
        self.assertEqual(result.status_code, 201)

    # Also test :
        # No display
        # invalid email
        # password mismatch
        # invalid url website
        # lang 1 char, lang 3 char
        # owner_id : None, Existing one, not exists, not accessible
        # status : Member, Member + quota, Invalid status

        # Test as client : should directly get 403
        # Test as member : shoul directly get 403
