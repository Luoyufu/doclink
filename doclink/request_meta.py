# -*- coding: utf-8 -*-

import copy

import uritemplate


class RequestMeta(dict):
    """传入session作为发送request参数来源

    每一个api实例有一个requestmeta作为享元
    调用api时，生成一个deepcopy供api构造参数
    """

    @property
    def copy(self):
        return copy.deepcopy(self)

    def get_url(self):
        path_args = self.get('path')
        uri_template = self['base_uri'] + self['uri']

        if path_args:
            return uritemplate.expand(uri_template, path_args)
        else:
            return uri_template


class RequestMetaContainer(object):

    def __init__(self):
        self._request_meta = None

    def initialize_request_meta(self, *args, **kwargs):
        self._request_meta = RequestMeta(*args, **kwargs)

    @property
    def request_meta_copy(self):
        return self._request_meta.copy

    @property
    def request_meta(self):
        return self._request_meta

    @request_meta.setter
    def request_meta(self, request_meta):
        self._request_meta = request_meta
