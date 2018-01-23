# -*- coding: utf-8 -*-

import unittest

from doclink.request_meta import (
    RequestMeta,
    RequestMetaContainer)


class RequestMetaTestCase(unittest.TestCase):

    def test_update_field(self):
        request_meta = RequestMeta()
        request_meta.update({'uri': 'uri'}, method='get')

        self.assertEqual(request_meta['uri'], 'uri')
        self.assertEqual(request_meta['method'], 'get')

    def test_init_with_field(self):
        request_meta = RequestMeta({'uri': 'uri'}, method='method')

        self.assertEqual(request_meta['uri'], 'uri')
        self.assertEqual(request_meta['method'], 'method')

    def test_copy(self):
        request_meta = RequestMeta({'uri': 'uri'}, method='method')
        copy = request_meta.copy

        self.assertEqual(copy, request_meta)
        self.assertIsNot(copy, request_meta)

    def test_get_url_with_path_arg(self):
        request_meta = RequestMeta(
            uri='uri/{arg1}',
            base_uri='https://base_uri/',
            path={'arg1': 'value1'})
        url = request_meta.get_url()

        self.assertEqual(url, 'https://base_uri/uri/value1')

    def test_get_url_without_path_arg(self):
        request_meta = RequestMeta(
            uri='uri',
            base_uri='https://base_uri/')
        url = request_meta.get_url()

        self.assertEqual(url, 'https://base_uri/uri')


class RequestMetaContainerTestCase(unittest.TestCase):

    def test_initialize_request_meta(self):
        request_meta_container = RequestMetaContainer()
        request_meta_container.initialize_request_meta(uri='uri')

        self.assertEqual(request_meta_container.request_meta['uri'], 'uri')

    def test_request_meta_copy(self):
        request_meta_container = RequestMetaContainer()
        request_meta_container.initialize_request_meta(uri='uri')

        request_meta_copy = request_meta_container.request_meta_copy

        self.assertIsNot(request_meta_container.request_meta, request_meta_copy)
        self.assertEqual(request_meta_copy['uri'], 'uri')
