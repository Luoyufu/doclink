# -*- coding: utf-8 -*-

import copy

from functools import reduce, partial
from operator import or_

from .request_meta import RequestMetaContainer
from .utils import raw_args_from_uri
from .meta_parser import creat_parser
from .arg import create_group


class Api(RequestMetaContainer):

    def __init__(self, name, consumer, http_method, uri, func):
        super(Api, self).__init__()
        self.name = name
        self.consumer = consumer
        self.func = func
        self.arg_groups = []
        self.request_meta = consumer.request_meta_copy
        self.request_meta.update(
            uri=uri,
            method=http_method)
        self.expected_status_code = consumer.expected_status_code
        self.resp_hooks = [consumer.hook]

    def add_resp_hook(self, hook):
        if not callable(hook):
            raise ValueError('resp_hook must be callable')

        self.resp_hooks.append(hook)

    def _handle_resp(self, resp):
        for resp_hook in self.resp_hooks:
            hook_result = resp_hook(resp)

            if hook_result is not None:
                return hook_result

        result = self.func(resp)
        if result is None:
            return resp
        else:
            return result

    def _enrich_resp(self, resp, kwargs):
        """Add some extra attrs to resp.

        Resp hook can use these extra attrs for process.
        """
        resp.caller = self
        resp.input_kwargs = kwargs

    def add_arg_group(self, arg_group):
        self.arg_groups.append(arg_group)

    def update_request_meta(self, *args, **kwargs):
        self.request_meta.update(*args, **kwargs)

    def __call__(self, **kwargs):
        input_kwargs = copy.copy(kwargs)
        request_meta = self.request_meta_copy

        # merge all the used_arg_set
        if self.arg_groups:
            used_arg_set = reduce(
                or_,
                (arg_group.process_request_meta(request_meta, input_kwargs)
                 for arg_group in self.arg_groups))

            for used_arg in used_arg_set:
                input_kwargs.pop(used_arg, None)

        request_meta.update(input_kwargs)
        resp = self.consumer.client.request(request_meta)
        self._enrich_resp(resp, kwargs)

        return self._handle_resp(resp)

    def partial(self, *args, **kwargs):
        return partial(self, *args, **kwargs)

    def routing(self, route_key):
        return self.partial(base_uri=self.consumer.get_routed_uri(route_key))


class ApiBuilder(object):

    def __init__(self, consumer, http_method, uri, func, parser, arg_validators=None):
        self._api = Api(func.__name__, consumer, http_method, uri, func)
        self.arg_validators = arg_validators
        self.parser = parser
        self.build_path_arg_group(uri)

    def build_path_arg_group(self, uri):
        path_raw_args = raw_args_from_uri(uri)
        if path_raw_args:
            self._api.add_arg_group(create_group('path', path_raw_args))

    def build_arg_group(self, group_name, raw_args):
        validators = None
        if self.arg_validators:
            validators = self.arg_validators.get(group_name)

        self._api.add_arg_group(create_group(group_name, raw_args, validators))

    def build_base_uri(self, base_uri):
        self._api.update_request_meta(base_uri=base_uri)

    def build_timeout(self, timeout):
        self._api.update_request_meta(timeout=timeout)

    def build_expected_status_code(self, status_code):
        self._api.expected_status_code = status_code

    def build(self):
        if self.parser:
            self.parser.set_builder(self)
            self.parser.parse()

        return self._api


def build_api(consumer, http_method, uri, func, arg_validators=None):
    parser = creat_parser(func.__doc__)
    builder = ApiBuilder(consumer, http_method, uri, func, parser, arg_validators)
    return builder.build()
