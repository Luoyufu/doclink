# -*- coding: utf-8 -*-

import pytest

from doclink.consumer import Consumer
from doclink.builder import Api


class MockClient(object):
    def request(self, request_meta):
        return MockResp(200)


class MockResp(object):
    def __init__(self, status_code):
        self.status_code = status_code


def mock_func(resp):
    pass


consumer = Consumer('base_uri', client=MockClient())


class TestApi(object):

    def test_init(self):
        api = Api('test', consumer, 'get', 'uri', mock_func)

        assert api.name == 'test'
        assert api.request_meta == {'base_uri': 'base_uri',
                                    'uri': 'uri',
                                    'method': 'get'}

    def test_update_request_meta(self):
        api = Api('test', consumer, 'get', 'uri', mock_func)
        api.update_request_meta(base_uri='new_base_uri')

        assert api.request_meta, {'base_uri': 'new_base_uri',
                                  'uri': 'uri',
                                  'method': 'get'}

    def test_add_arg_group(self):
        arg_group = object()
        api = Api('test', consumer, 'get', 'uri', mock_func)
        api.add_arg_group(arg_group)

        assert arg_group in api.arg_groups

    def test_partial(self):
        api = Api('test', consumer, 'get', 'uri', mock_func)
        p = api.partial(arg='value')

        assert p.args == ()
        assert p.keywords == {'arg': 'value'}
        assert p.func is api

    def test_resp_hook(self):
        def mock_hook(resp):
            return resp.status_code

        api = Api('test', consumer, 'get', 'uri', mock_func)
        api.add_resp_hook(mock_hook)

        result = api()

        assert result == 200

    def test_resp_hook_not_callable(self):
        api = Api('test', consumer, 'get', 'uri', mock_func)

        with pytest.raises(ValueError):
            api.add_resp_hook(None)
