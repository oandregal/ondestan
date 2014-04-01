# coding=UTF-8
import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from ondestan.views import viewer
        request = testing.DummyRequest()
        info = viewer(request)
        self.assertEqual(info['project'], 'Ondestán')
