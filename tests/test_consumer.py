# -*- coding: utf-8 -*-

import unittest

from doclink import Consumer
from doclink.consumer import Route
from doclink.exceptions import StatusCodeUnexpectedError


class MockResp(object):
    def __init__(self, status_code):
        self.status_code = status_code


class MockApi(object):

    def __init__(self, status_code=200):
        self.expected_status_code = status_code

    def partial(self, base_uri):
        return base_uri


class ConsumerTestCase(unittest.TestCase):

    def test_api_deco_invalid_arg_validators(self):
        cs = Consumer('http://test')

        with self.assertRaises(ValueError):
            @cs.get('/uri', arg_validators=['test'])
            def api_func(resp):
                pass

    def test_api_deco_invalid_on_request(self):
        cs = Consumer('http://test')

        with self.assertRaises(ValueError):
            @cs.get('/uri', on_request=['test'])
            def api_func(resp):
                pass

    def test_check_status_expect(self):
        api = MockApi(200)
        resp = MockResp(200)
        resp.caller = api
        resp.input_kwargs = None

        Consumer._check_status(resp)

    def test_check_status_not_expect(self):
        api = MockApi(200)
        resp = MockResp(401)
        resp.caller = api
        resp.input_kwargs = None

        with self.assertRaises(StatusCodeUnexpectedError):
            Consumer._check_status(resp)

    def test_check_status_code_is_str(self):
        api = MockApi(200)
        resp = MockResp('200')

        resp.caller = api
        resp.input_kwargs = None

        Consumer._check_status(resp)

    def test_hook_with_return(self):
        api = MockApi(200)
        resp = MockResp(200)
        resp.caller = api
        resp.input_kwargs = None
        resp.hook1_hooked = False
        resp.hook2_hooked = False
        consumer = Consumer('base_uri')

        @consumer.resp_hook
        def hook1(resp):
            resp.hook1_hooked = True

            return resp

        @consumer.resp_hook
        def hook2(resp):
            resp.hook2_hooked = True

        result = consumer.hook(resp)

        self.assertIs(result, resp)
        self.assertEqual(resp.hook1_hooked, True)
        self.assertEqual(result.hook2_hooked, False)

    def test_hook_without_return(self):
        api = MockApi(200)
        resp = MockResp(200)
        resp.hook1_hooked = False
        resp.hook2_hooked = False

        resp.caller = api
        resp.input_kwargs = None
        consumer = Consumer('base_uri')

        @consumer.resp_hook
        def hook1(resp):
            resp.hook1_hooked = True

        @consumer.resp_hook
        def hook2(resp):
            resp.hook2_hooked = True

        result = consumer.hook(resp)

        self.assertIs(result, None)
        self.assertEqual(resp.hook1_hooked, True)
        self.assertEqual(resp.hook2_hooked, True)

    def test_routing_on_route_key(self):
        consumer = Consumer('base_uri')
        consumer.router = {
            'key1': 'base_uri1',
            'key2': 'base_uri2'
        }

        route = consumer.routing('key1')

        assert route.base_uri == 'base_uri1'

    def test_routing_on_default(self):
        consumer = Consumer('base_uri')
        consumer.router = {
            'key1': 'base_uri1',
            'key2': 'base_uri2'
        }

        route = consumer.routing('other_key')

        assert route.base_uri == 'base_uri'

    def test_route(self):
        api1 = MockApi()
        api2 = MockApi()

        consumer = Consumer('base_uri')

        consumer.apis['api1'] = api1
        consumer.apis['api2'] = api2

        route = Route(consumer, 'selected_uri')

        assert route.api1 == 'selected_uri'
