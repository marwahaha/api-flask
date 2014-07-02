# coding:utf-8

from tests import BaseTestCase
import json

class TestList(BaseTestCase):
    __display__ = "Members > Listing (admin)"

    def setUp(self):
        self.mode = 'admin'

    def test_listing_generic(self):
        """Test with no parameters"""

        result = self.get('/v1/members/')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) > 0)

    def test_listing_filter_by_display_like(self):
        """Test with display like"""

        result = self.get('/v1/members/?display=ad%')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) == 1)


    def test_listing_filter_by_display(self):
        """Test with display full"""

        result = self.get('/v1/members/?display=administrator')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) == 1)

    def test_listing_order_by_seen_asc(self):
        """Test with ordering by seen asc"""

        result = self.get('/v1/members/?order_by=seen')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) > 0)

        self.assertTrue(data['items'][0]['seen'] <= data['items'][1]['seen'])

    def test_listing_order_by_seen_desc(self):
        """Test with ordering by seen desc"""

        result = self.get('/v1/members/?order_by=-seen')
        self.assertEqual(result.status_code, 200)

        data = json.loads(result.data)
        self.assertTrue(len(data['items']) > 0)

        self.assertTrue(data['items'][0]['seen'] >= data['items'][1]['seen'])

    def test_listing_order_by_invalid(self):
        """Test with ordering by invalid"""

        result = self.get('/v1/members/?order_by=hello')
        self.assertEqual(result.status_code, 400)

        data = json.loads(result.data)
        self.assertIsNotNone(data['order_by'])
