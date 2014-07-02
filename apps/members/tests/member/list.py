# coding:utf-8

from tests import BaseTestCase
import json

class TestList(BaseTestCase):
    __display__ = "Members > Listing (member)"

    def setUp(self):
        self.mode = 'member'

    def test_listing_generic_member(self):
        """Test with no parameters"""

        result = self.get('/v1/members/')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) > 0)