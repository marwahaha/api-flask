# coding:utf-8

from tests import BaseTestCase
import json

class TestCreate(BaseTestCase):
    __display__ = "Members > Create (member)"

    def setUp(self):
    	self.mode = 'member'
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

    def test_create_client_member(self):
        """Test creating a client"""
        self.data['email'] = 'member@example.com'
        result = self.post("/v1/members/", data=self.data)
        self.assertEqual(result.status_code, 201)

    def test_create_member_member(self):
        """Test creating a member"""
        self.data['email'] = 'member@example.com'
        self.data['status'] = 'MEMBER'
        result = self.post("/v1/members/", data=self.data)
        self.assertEqual(result.status_code, 403)


    # Also test :
        # No display
        # invalid email
        # password mismatch
        # invalid url website
        # lang 1 char, lang 3 char
        # owner_id : None, Existing one, not exists, not accessible
        # status : Member, Member + quota, Invalid status
