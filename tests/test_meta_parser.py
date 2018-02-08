# -*- coding: utf-8 -*-

import unittest

from doclink import meta_parser
from doclink.exceptions import InvalidApimetaItemError


class FakeBuilder(object):
    def build_arg_group(self, group_name, raw_args):
        self.arg_group_name = {group_name: raw_args}

    def build_base_uri(self, base_uri):
        self.base_uri = base_uri

    def build_timeout(self, timeout):
        self.timeout = timeout

    def build_expected_status_code(self, status):
        self.expected_status_code = status


class TestParseObserver(unittest.TestCase):

    def test_map_event_handle(self):
        event_handle_map = meta_parser.ParseObserver.event_handle_map

        self.assertIn('arg_group', event_handle_map)
        self.assertIn('base_uri', event_handle_map)
        self.assertIn('timeout', event_handle_map)
        self.assertIn('expected_status_code', event_handle_map)

    def test_trigger_event(self):
        builder = FakeBuilder()

        parse_observer = meta_parser.ParseObserver()
        parse_observer.set_builder(builder)
        parse_observer.trigger_event('arg_group', 'group_name', 'arg1')
        parse_observer.trigger_event('base_uri', 'base_uri')
        parse_observer.trigger_event('timeout', 30)
        parse_observer.trigger_event('expected_status_code', 200)

        self.assertEqual(builder.arg_group_name, {'group_name': 'arg1'})
        self.assertEqual(builder.base_uri, 'base_uri')
        self.assertEqual(builder.timeout, 30)
        self.assertEqual(builder.expected_status_code, 200)

    def test_trigger_event_invalid(self):
        builder = FakeBuilder()

        parse_observer = meta_parser.ParseObserver()
        parse_observer.set_builder(builder)

        with self.assertRaises(InvalidApimetaItemError):
            parse_observer.trigger_event('invalid', 'invalid')


class TestParserFactory(unittest.TestCase):

    def test_register_parser_with_name(self):
        @meta_parser.ParserFactory.register_parser('test')
        class TestParser(meta_parser.ParserBase):
            pass

        self.assertEqual(
            meta_parser.ParserFactory._parser_map['test'],
            TestParser)

        del meta_parser.ParserFactory._parser_map['test']

    def test_register_parser_without_name(self):
        @meta_parser.ParserFactory.register_parser
        class TestParser(meta_parser.ParserBase):
            pass

        self.assertEqual(
            meta_parser.ParserFactory._parser_map['TestParser'],
            TestParser)

        del meta_parser.ParserFactory._parser_map['TestParser']

    def test_create(self):
        @meta_parser.ParserFactory.register_parser('test')
        class TestParser(meta_parser.ParserBase):
            pass

        pydoc = """
            <meta:test>
                timeout: 30
            </meta>
        """
        parser = meta_parser.ParserFactory.create(pydoc)

        self.assertIsInstance(parser, TestParser)

        del meta_parser.ParserFactory._parser_map['test']

    def test_create_with_default(self):
        pydoc = """
        <meta>
            timeout: 30
        </meta>
        """
        parser = meta_parser.ParserFactory.create(pydoc)

        self.assertIsInstance(parser, meta_parser.YamlParser)


class ParserBasesTestCase(unittest.TestCase):

    def test_set_builder(self):
        meta_doc = """
        timeout: 30
        """

        class Observer(object):
            def set_builder(self, builder):
                self.builder = builder

        builder = object()
        observer = Observer()

        parser = meta_parser.ParserBase(meta_doc, observer)
        parser.set_builder(builder)

        self.assertEqual(observer.builder, builder)


class YamlParserTestCase(unittest.TestCase):

    def test_parse(self):
        class Builder(object):
            def __init__(self):
                self.events = {}

            def build(self, event, *args):
                self.events[event] = args

        class Observer(object):
            def set_builder(self, builder):
                self.builder = builder

            def trigger_event(self, event_name, *args):
                self.builder.build(event_name, *args)

        meta_doc = """
        timeout: 30
        args:
            query:
                - client_id
        """

        observer = Observer()
        builder = Builder()
        parser = meta_parser.YamlParser(meta_doc, observer)
        parser.set_builder(builder)

        parser.parse()

        self.assertEqual(
            builder.events,
            {'arg_group': ('params', ['client_id']),
             'timeout': (30,)})
