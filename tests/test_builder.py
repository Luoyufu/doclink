# -*- coding: utf-8 -*-

import unittest

from doclink.consumer import Consumer
from doclink.builder import Api


class MockClient(object):
    pass


class MockResp(object):
    def __init__(self, status_code):
        self.status_code = status_code


def test_func(resp):
    pass


consumer = Consumer('base_uri', client=MockClient())


class ApiTestCase(unittest.TestCase):

    def test_init(self):
        api = Api('test', consumer, 'get', 'uri', test_func)

        self.assertEqual(api.name, 'test')
        self.assertEqual(
            api.request_meta,
            {'base_uri': 'base_uri',
             'uri': 'uri',
             'method': 'get'})

    def test_update_request_meta(self):
        api = Api('test', consumer, 'get', 'uri', test_func)
        api.update_request_meta(base_uri='new_base_uri')

        self.assertEqual(
            api.request_meta,
            {'base_uri': 'new_base_uri',
             'uri': 'uri',
             'method': 'get'})
