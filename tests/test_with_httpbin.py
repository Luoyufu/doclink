# -*- coding: utf-8 -*-

import pytest

from doclink import Consumer
from doclink.exceptions import StatusCodeUnexpectedError
from doclink import jsonify


@pytest.fixture(scope='module')
def consumer():
    class OnRequest(object):

        def __init__(self):
            self.called = False

        def __call__(self, request_meta):
            self.called = True

    on_request = OnRequest()

    consumer = Consumer('http://httpbin.org')

    @jsonify
    @consumer.get('/basic-auth/{username}/{password}',
                  on_request=on_request)
    def basic_auth(resp):
        """
        <meta>
            args:
                auth
        </meta>
        """

    @jsonify
    @consumer.post('/post')
    def form_post(resp):
        """
        <meta>
            args:
                form:
                    - field1
                    - field2
        </meta>
        """

    @jsonify
    @consumer.post('/post')
    def file_post(resp):
        """
        <meta>
            args:
                file:
                    - file
        </meta>
        """

    @consumer.get('/status/{status_code=404}')
    def unexpected_status_code(resp):
        """
        <meta>
            expected_status_code: 200
        </meta>
        """
        return resp.status_code

    return consumer


class TestDoclink(object):

    def test_basic_auth(self, consumer):
        resp_json = consumer.basic_auth(username='user', password='passwd')

        assert consumer.basic_auth._on_request.called
        assert resp_json == {'authenticated': True, 'user': 'user'}

    def test_forms_post(self, consumer):
        resp_json = consumer.form_post(field1=1, field2=2)

        assert resp_json['form'] == {'field1': '1', 'field2': '2'}

    def test_file_post(self, consumer):
        resp_json = consumer.file_post(file=('file_name', 'str_file'))

        assert resp_json['files'] == {'file': 'str_file'}

    def test_status_code(self, consumer):
        with pytest.raises(StatusCodeUnexpectedError):
            consumer.unexpected_status_code()
