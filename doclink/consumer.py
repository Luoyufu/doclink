# -*- coding: utf-8 -*-

from functools import partial

from .builder import build_api
from .request_meta import RequestMetaContainer
from .utils import methods
from .clients import DefaultClient
from .exceptions import StatusCodeUnexpectedError


class Consumer(RequestMetaContainer):
    """docstring for ConsumerBase"""

    router = None

    def __init__(self, base_uri, expected_status_code=None, client=None, **meta_kwargs):
        super(Consumer, self).__init__()
        self.base_uri = base_uri
        self.initialize_request_meta(base_uri=base_uri, **meta_kwargs)
        self.apis = {}
        self.resp_hooks = [self._check_status]
        self.client = client or DefaultClient()
        self._router = None
        self.expected_status_code = expected_status_code

    @staticmethod
    def _check_status(resp):
        api = resp.caller
        if api.expected_status_code is not None:
            status_code = resp.status_code

            if int(status_code) != api.expected_status_code:
                raise StatusCodeUnexpectedError(api.expected_status_code, status_code, resp)

    def hook(self, resp):
        for resp_hook in self.resp_hooks:
            result = resp_hook(resp)
            if result is not None:
                return result

    def api(self, http_method, uri, arg_validators=None):
        """decorator to create an api"""
        if arg_validators is not None:
            if not isinstance(arg_validators, dict):
                raise ValueError('arg_validators should be a dict instance')

        def deco(func):
            name = func.__name__
            api = build_api(self, http_method, uri, func, arg_validators)

            self.apis[name] = api

            return api
        return deco

    def resp_hook(self, func):
        self.resp_hooks.append(func)
        return func

    @property
    def router(self):
        return self._router

    @router.setter
    def router(self, router):
        self._router = router

    def routing(self, route_key):
        return Route(self, base_uri=self.get_routed_uri(route_key))

    def get_routed_uri(self, route_key):
        if self.router:
            return self.router.get(route_key) or self.base_uri
        else:
            return self.base_uri

    def __getattr__(self, name):
        if name in methods:
            return partial(self.api, name)

        if name in self.apis:
            return self.apis[name]

        raise KeyError(name)


class Route(object):

    def __init__(self, consumer, base_uri):
        self.consumer = consumer
        self.base_uri = base_uri

    def __getattr__(self, name):
        api = self.consumer.apis[name]
        return api.partial(base_uri=self.base_uri)
