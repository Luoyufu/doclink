# -*- coding: utf-8 -*-

import unittest

from doclink.consumer import Consumer


class DoclinkTestCase(unittest.TestCase):

    def test_basic_auth(self):
        consumer = Consumer('http://http.org/')

        @consumer.resp_hook
        def print_hook(resp):
            print(resp.status_code)

        consumer.router = {'bin': 'http://httpbin.org/'}

        @consumer.get('basic-auth/{username}/{password}')
        def basic_auth(resp):
            """
            <meta>
                args:
                    auth
            </meta>
            """
            return resp.json()

        resp_json = basic_auth.routing('bin')(username='user', password='passwd')

        print(resp_json)
