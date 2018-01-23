# -*- coding: utf-8 -*-

import unittest

from doclink import arg
from doclink import utils
from doclink.exceptions import RequiredArgMissingError
from doclink.request_meta import RequestMeta


class ArgTestCase(unittest.TestCase):
    raw = utils.RawArg(**{
        'name': 'name',
        'alias': 'alias',
        'required': True,
        'default': 'default'
    })
    raw_with_alias = utils.RawArg(**{
        'name': 'name',
        'alias': 'alias',
        'required': True,
        'default': None
    })
    raw_required_with_default = utils.RawArg(**{
        'name': 'name',
        'alias': None,
        'required': True,
        'default': 'default'
    })
    raw_required_without_default = utils.RawArg(**{
        'name': 'name',
        'alias': None,
        'required': True,
        'default': None
    })
    raw_not_required_with_default = utils.RawArg(**{
        'name': 'name',
        'alias': None,
        'required': False,
        'default': 'default'
    })
    raw_not_required_without_default = utils.RawArg(**{
        'name': 'name',
        'alias': None,
        'required': False,
        'default': None
    })

    def test_arg_from_raw(self):
        arg_ = arg.Arg.from_raw(self.raw)

        self.assertEqual(arg_.name, 'name')
        self.assertEqual(arg_.alias, 'alias')
        self.assertEqual(arg_.required, True)
        self.assertEqual(arg_.default, 'default')

    def test_arg_raw_dict(self):
        arg_ = arg.Arg.from_raw(self.raw)

        self.assertEqual(
            arg_.raw_dict,
            {'name': 'name',
             'alias': 'alias',
             'required': True,
             'default': 'default'})

    def test_output_raw_with_alias(self):
        arg_ = arg.Arg(*self.raw_with_alias)
        input_kwargs = {'alias': 'value', 'other': 'other'}
        output = arg_.output({}, input_kwargs)

        self.assertEqual(output, ('alias', 'value'))
        self.assertEqual(input_kwargs, {'alias': 'value', 'other': 'other'})

        with self.assertRaises(RequiredArgMissingError):
            arg_.output({}, {'name': 'value'})

    def test_output_raw_required_with_default(self):
        arg_ = arg.Arg(*self.raw_required_with_default)
        output = arg_.output({}, {'name': 'value'})

        self.assertEqual(output, ('name', 'value'))

        output = arg_.output({}, {'other': 'other'})

        self.assertEqual(output, ('name', 'default'))

    def test_output_raw_required_without_default(self):
        arg_ = arg.Arg(*self.raw_required_without_default)
        output = arg_.output({}, {'name': 'value'})

        self.assertEqual(output, ('name', 'value'))

        with self.assertRaises(RequiredArgMissingError):
            arg_.output({}, {'other': 'other'})

    def test_output_raw_not_required_with_default(self):
        arg_ = arg.Arg(*self.raw_not_required_with_default)
        output = arg_.output({}, {'other': 'other'})

        self.assertEqual(output, ('name', 'default'))

    def test_output_raw_not_required_without_default(self):
        arg_ = arg.Arg(*self.raw_not_required_without_default)
        output = arg_.output({}, {'other': 'other'})

        self.assertEqual(output, ('name', utils.NoInput))

    def test_outpu_raw_required_with_value_in_current_kwargs_noinput(self):
        arg_ = arg.Arg(*self.raw_required_without_default)
        current_kwargs = {'name': 'value'}
        output = arg_.output(current_kwargs, {'other': 'other'})

        self.assertEqual(output, ('name', 'value'))

    def test_outpu_raw_required_with_value_in_current_kwargs_input(self):
        arg_ = arg.Arg(*self.raw_required_without_default)
        current_kwargs = {'name': 'value'}
        output = arg_.output(current_kwargs, {'name': 'other'})

        self.assertEqual(output, ('name', 'other'))

    def test_add_validator_with_callable(self):
        def raise_validator(arg, value):
            raise ValueError

        arg_ = arg.Arg(*self.raw)
        arg_.add_validator(raise_validator)

        with self.assertRaises(ValueError):
            arg_.output({}, {'name': 'value'})

    def test_add_validator_without_callable(self):
        arg_ = arg.Arg(*self.raw)

        with self.assertRaises(ValueError):
            arg_.add_validator('test')


class ArgGroupTestCase(unittest.TestCase):

    def test_arg_group_registry(self):
        @arg.register_arg_group('test')
        class TestArgGroup(arg.ArgGroup):
            pass

        self.assertIsInstance(arg.create_group('test', 'arg'), TestArgGroup)

        arg.unregister_arg_group('test')
        with self.assertRaises(ValueError):
            arg.create_group('test', 'test')

    def test_arg_group_init_with_validators(self):
        raw_args = ['arg1', {'arg2': 'value2_default'}]

        def callback(arg, value):
            pass

        arg_group = arg.ArgGroup(
            'params',
            raw_args,
            validators={
                'arg1': callback,
                'arg2': callback})

        self.assertIn(callback, arg_group.arg_map['arg1']._validators)
        self.assertIn(callback, arg_group.arg_map['arg2']._validators)

    def test_process_request_meta(self):
        raw_args = ['arg1', {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg1': 'other1', 'arg4': 'value4'})
        input_kwargs = dict(arg1='value1', arg2='value2', arg3='value3')

        arg_group.process_request_meta(request_meta, input_kwargs)
        self.assertEqual(request_meta['params'],
                         {'arg1': 'value1',
                          'arg2': 'value2',
                          'arg4': 'value4'})

    def test_process_request_meta_required_arg_missing(self):
        raw_args = ['arg1', {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg4': 'value4'})
        input_kwargs = dict(arg2='value2')

        with self.assertRaises(RequiredArgMissingError):
            arg_group.process_request_meta(request_meta, input_kwargs)

    def test_process_request_meta_not_required_arg_missing(self):
        raw_args = [{'arg1': {'required': False}}, {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg4': 'value4'})
        input_kwargs = dict(arg2='value2', arg3='value3')
        arg_group.process_request_meta(request_meta, input_kwargs)

        self.assertNotIn('arg1', request_meta)


class PredefinedArgGroupTestCase(unittest.TestCase):

    def test_arg_predefine_create_arg(self):
        arg_predefine = arg.ArgPredefine(name='name', default='basic', choices=['basic', 'digest'])
        arg_ = arg_predefine.create_arg()

        self.assertEqual(arg_.name, 'name')
        self.assertEqual(arg_.default, 'basic')
        self.assertEqual(arg_.required, True)
        self.assertEqual(arg_.alias, None)

    def test_arg_predefine_default_not_in_choices(self):
        with self.assertRaises(ValueError):
            arg.ArgPredefine(name='name', default='ohter', choices=['basic', 'digest'])

    def test_predefined_arg_group_init(self):
        class TestGroup(arg.PredefinedArgGroup):
            arg1 = arg.ArgPredefine(default='default')
            arg2 = arg.ArgPredefine()

        def callback(arg, value):
            pass

        test_group = TestGroup('params', {'arg1': 'value1'},
                               validators={'arg1': callback,
                                           'arg2': callback})

        self.assertEqual(test_group.arg1.raw_dict,
                         {'name': 'arg1',
                          'required': True,
                          'default': 'value1',
                          'alias': None})
        self.assertEqual(test_group.arg2.raw_dict,
                         {'name': 'arg2',
                          'required': True,
                          'default': None,
                          'alias': None})
        self.assertIn(callback, test_group.arg1._validators)
        self.assertIn(callback, test_group.arg2._validators)

    def test_process_request_meta(self):
        class TestGroup(arg.PredefinedArgGroup):
            arg1 = arg.ArgPredefine(default='default')
            arg2 = arg.ArgPredefine()
            arg3 = arg.ArgPredefine(required=False)

        test_group = TestGroup('params', {'arg1': 'value1'})
        request_meta = RequestMeta(params={'arg2': 'current_value2'})
        input_kwargs = dict(arg2='new_value2')

        test_group.process_request_meta(request_meta, input_kwargs)

        self.assertEqual(request_meta['params'],
                         {'arg1': 'value1',
                          'arg2': 'new_value2'})

    def test_process_request_meta_input_no_in_choices(self):
        class TestGroup(arg.PredefinedArgGroup):
            arg1 = arg.ArgPredefine(choices=['value1', 'value2'])

        test_group = TestGroup('params')
        request_meta = RequestMeta()
        input_kwargs = dict(arg1='other')

        with self.assertRaises(ValueError):
            test_group.process_request_meta(request_meta, input_kwargs)


class AuthArgGroupTestCase(unittest.TestCase):

    def test_create_arg_group(self):
        auth_group = arg.create_group(
            'auth',
            [{'type': 'digest'},
             {'username': {'alias': 'alias_username'}}])

        self.assertEqual(auth_group.type.raw_dict,
                         {'name': 'type',
                          'default': 'digest',
                          'required': True,
                          'alias': None})
        self.assertEqual(auth_group.username.raw_dict,
                         {'name': 'username',
                          'default': None,
                          'alias': 'alias_username',
                          'required': True})
        self.assertEqual(auth_group.password.raw_dict,
                         {'name': 'password',
                          'default': None,
                          'alias': None,
                          'required': True})

    def test_process_request_meta(self):
        auth_group = arg.create_group(
            'auth',
            [{'type': 'digest'}])

        request_meta = RequestMeta(
            auth={'type': 'basic',
                  'username': 'current_username'})
        input_kwargs = dict(username='username', password='password')
        auth_group.process_request_meta(request_meta, input_kwargs)

        self.assertEqual(request_meta['auth'],
                         {'type': 'digest',
                          'username': 'username',
                          'password': 'password'})
