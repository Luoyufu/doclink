# -*- coding: utf-8 -*-

from doclink.request_meta import (
    RequestMeta,
    RequestMetaContainer)


class TestRequestMeta(object):

    def test_update_field(self):
        request_meta = RequestMeta()
        request_meta.update({'uri': 'uri'}, method='get')

        assert request_meta['uri'] == 'uri'
        assert request_meta['method'] == 'get'

    def test_init_with_field(self):
        request_meta = RequestMeta({'uri': 'uri'}, method='method')

        assert request_meta['uri'] == 'uri'
        assert request_meta['method'] == 'method'

    def test_copy(self):
        request_meta = RequestMeta({'uri': 'uri'}, method='method')
        copy = request_meta.copy

        assert copy == request_meta
        assert copy is not request_meta

    def test_get_url_with_path_arg(self):
        request_meta = RequestMeta(
            uri='uri/{arg1}',
            base_uri='https://base_uri/',
            path={'arg1': 'value1'})
        url = request_meta.get_url()

        assert url == 'https://base_uri/uri/value1'

    def test_get_url_without_path_arg(self):
        request_meta = RequestMeta(
            uri='uri',
            base_uri='https://base_uri/')
        url = request_meta.get_url()

        assert url == 'https://base_uri/uri'


class TestRequestMetaContainer(object):

    def test_initialize_request_meta(self):
        request_meta_container = RequestMetaContainer()
        request_meta_container.initialize_request_meta(uri='uri')

        assert request_meta_container.request_meta['uri'] == 'uri'

    def test_request_meta_copy(self):
        request_meta_container = RequestMetaContainer()
        request_meta_container.initialize_request_meta(uri='uri')

        request_meta_copy = request_meta_container.request_meta_copy

        assert request_meta_container.request_meta is not request_meta_copy
        assert request_meta_copy['uri'] == 'uri'
