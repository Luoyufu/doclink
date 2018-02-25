# -*- coding: utf-8 -*-

import pytest

from doclink.decorators import jsonify
from doclink.consumer import Consumer


class MockClient(object):
    def request(self, request_meta):
        return MockResp(200)


class MockResp(object):
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {'key': 'value'}


def mock_func(resp):
    pass


@pytest.fixture
def consumer():
    return Consumer('base_uri', client=MockClient())


def test_jsonify(consumer):
    @jsonify
    @consumer.post('/uri')
    def func(resp):
        pass

    with pytest.raises(ValueError):
        jsonify(lambda x: x)

    assert func() == {'key': 'value'}
