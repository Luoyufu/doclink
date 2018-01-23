# -*- coding: utf-8 -*-

from functools import partial
import re

import yaml

from .exceptions import (
    ApimetaNotFoundError,
    MetaParserUnknownError,
    InvalidApimetaItemError)


class ParseObserver(object):

    event_handle_map = {}

    def __init__(self):
        self._builder = None

    @classmethod
    def map_event_handle(cls):
        cls.event_handle_map.update(
            arg_group=cls._on_arg_group,
            base_uri=cls._on_base_uri,
            timeout=cls._on_timeout,
            expected_status_code=cls._on_expected_status_code)

    def trigger_event(self, event_name, *args, **kwargs):
        try:
            unbound_method = self.event_handle_map[event_name]
        except KeyError:
            raise InvalidApimetaItemError(event_name)

        unbound_method(self, *args, **kwargs)

    def _on_arg_group(self, group_name, raw_agrs):
        self._builder.build_arg_group(group_name, raw_agrs)

    def _on_base_uri(self, value):
        self._builder.build_base_uri(value)

    def _on_timeout(self, value):
        self._builder.build_timeout(value)

    def _on_expected_status_code(self, value):
        self._builder.build_expected_status_code(value)

    def set_builder(self, builder):
        self._builder = builder


ParseObserver.map_event_handle()


class ParserFactory(object):
    meta_pattern = re.compile(r'\<meta(?:\:(?P<format>\w+))?\>(?P<meta>.+)\</meta\>',
                              re.DOTALL)
    _parser_map = {}

    @classmethod
    def register_parser(cls, parser_or_name):

        def real_register(parser_cls, name=None):
            name = name or parser_cls.__name__
            cls._parser_map[name] = parser_cls

            return parser_cls

        if isinstance(parser_or_name, str):
            return partial(real_register, name=parser_or_name)
        else:
            assert issubclass(parser_or_name, ParserBase), 'parser required'
            return real_register(parser_or_name)

    @classmethod
    def _extract(cls, pydoc):
        if pydoc is None:
            raise ApimetaNotFoundError()

        match = cls.meta_pattern.search(pydoc)
        if not match:
            raise ApimetaNotFoundError()

        return match.groups()

    @classmethod
    def create(cls, pydoc, observer=None):
        observer = observer or ParseObserver()
        try:
            format_, meta_doc = cls._extract(pydoc)
        except ApimetaNotFoundError:
            return None

        format_ = format_ or 'yaml'

        try:
            parser_cls = cls._parser_map[format_]
        except KeyError:
            raise MetaParserUnknownError(format_)
        else:
            return parser_cls(meta_doc, observer)


class ParserBase(object):

    def __init__(self, meta_doc, observer):
        self.meta_doc = meta_doc
        self.observer = observer

    def parse(self):
        raise NotImplementedError

    def set_builder(self, builder):
        self.observer.set_builder(builder)


@ParserFactory.register_parser('yaml')
class YamlParser(ParserBase):
    arg_field_map = {
        'query': 'params',
        'form': 'data',
        'header': 'headers',
        'file': 'files'
    }

    def parse(self):
        meta_dict = yaml.load(self.meta_doc)
        for item_name, item_value in meta_dict.items():
            if item_name == 'args':
                item_value = {item_value: None} if isinstance(item_value, str) else item_value
                for group_name, raw_agrs in item_value.items():
                    group_name = self.arg_field_map.get(group_name) or group_name
                    self.observer.trigger_event('arg_group', group_name, raw_agrs)
            else:
                self.observer.trigger_event(item_name, item_value)


def creat_parser(pydoc, observer=None):
    return ParserFactory.create(pydoc, observer)
