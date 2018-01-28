# -*- coding: utf-8 -*-

import pytest

from doclink import arg
from doclink import utils
from doclink.exceptions import RequiredArgMissingError
from doclink.request_meta import RequestMeta


@pytest.fixture(scope='class')
def raw_args():
    return dict(
        raw=utils.RawArg(**{
            'name': 'name',
            'alias': 'alias',
            'required': True,
            'default': 'default'
        }),
        raw_with_alias=utils.RawArg(**{
            'name': 'name',
            'alias': 'alias',
            'required': True,
            'default': None
        }),
        raw_required_with_default=utils.RawArg(**{
            'name': 'name',
            'alias': None,
            'required': True,
            'default': 'default'
        }),
        raw_required_without_default=utils.RawArg(**{
            'name': 'name',
            'alias': None,
            'required': True,
            'default': None
        }),
        raw_not_required_with_default=utils.RawArg(**{
            'name': 'name',
            'alias': None,
            'required': False,
            'default': 'default'
        }),
        raw_not_required_without_default=utils.RawArg(**{
            'name': 'name',
            'alias': None,
            'required': False,
            'default': None
        }))


class TestArg(object):

    def test_arg_from_raw(self, raw_args):
        arg_ = arg.Arg.from_raw(raw_args['raw'])

        assert arg_.name == 'name'
        assert arg_.alias == 'alias'
        assert arg_.required is True
        assert arg_.default == 'default'

    def test_arg_raw_dict(self, raw_args):
        arg_ = arg.Arg.from_raw(raw_args['raw'])

        assert arg_.raw_dict == {'name': 'name',
                                 'alias': 'alias',
                                 'required': True,
                                 'default': 'default'}

    def test_output_raw_with_alias(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_with_alias'])
        input_kwargs = {'alias': 'value', 'other': 'other'}
        output = arg_.output({}, input_kwargs)

        assert output == ('alias', 'value')
        assert input_kwargs == {'alias': 'value', 'other': 'other'}

        with pytest.raises(RequiredArgMissingError):
            arg_.output({}, {'name': 'value'})

    def test_output_raw_required_with_default(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_required_with_default'])
        output = arg_.output({}, {'name': 'value'})

        assert output == ('name', 'value')

        output = arg_.output({}, {'other': 'other'})

        assert output == ('name', 'default')

    def test_output_raw_required_without_default(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_required_without_default'])
        output = arg_.output({}, {'name': 'value'})

        assert output == ('name', 'value')

        with pytest.raises(RequiredArgMissingError):
            arg_.output({}, {'other': 'other'})

    def test_output_raw_not_required_with_default(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_not_required_with_default'])
        output = arg_.output({}, {'other': 'other'})

        assert output == ('name', 'default')

    def test_output_raw_not_required_without_default(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_not_required_without_default'])
        output = arg_.output({}, {'other': 'other'})

        assert output == ('name', utils.NoInput)

    def test_outpu_raw_required_with_value_in_current_kwargs_noinput(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_required_without_default'])
        current_kwargs = {'name': 'value'}
        output = arg_.output(current_kwargs, {'other': 'other'})

        assert output == ('name', 'value')

    def test_outpu_raw_required_with_value_in_current_kwargs_input(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw_required_without_default'])
        current_kwargs = {'name': 'value'}
        output = arg_.output(current_kwargs, {'name': 'other'})

        assert output == ('name', 'other')

    def test_add_validator_with_callable(self, raw_args):
        def raise_validator(arg, value):
            raise ValueError

        arg_ = arg.Arg(*raw_args['raw'])
        arg_.add_validator(raise_validator)

        with pytest.raises(ValueError):
            arg_.output({}, {'name': 'value'})

    def test_add_validator_without_callable(self, raw_args):
        arg_ = arg.Arg(*raw_args['raw'])

        with pytest.raises(ValueError):
            arg_.add_validator('test')


class TestArgGroup(object):

    def test_arg_group_registry(self):
        @arg.register_arg_group('test')
        class TestArgGroup(arg.ArgGroup):
            pass

        assert isinstance(arg.create_group('test', 'arg'), TestArgGroup)

        arg.unregister_arg_group('test')
        with pytest.raises(ValueError):
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

        assert callback in arg_group.arg_map['arg1']._validators
        assert callback in arg_group.arg_map['arg2']._validators

    def test_process_request_meta(self):
        raw_args = ['arg1', {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg1': 'other1', 'arg4': 'value4'})
        input_kwargs = dict(arg1='value1', arg2='value2', arg3='value3')

        arg_group.process_request_meta(request_meta, input_kwargs)
        assert request_meta['params'] == {'arg1': 'value1',
                                          'arg2': 'value2',
                                          'arg4': 'value4'}

    def test_process_request_meta_required_arg_missing(self):
        raw_args = ['arg1', {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg4': 'value4'})
        input_kwargs = dict(arg2='value2')

        with pytest.raises(RequiredArgMissingError):
            arg_group.process_request_meta(request_meta, input_kwargs)

    def test_process_request_meta_not_required_arg_missing(self):
        raw_args = [{'arg1': {'required': False}}, {'arg2': 'value2_default'}]
        arg_group = arg.ArgGroup('params', raw_args)
        request_meta = RequestMeta(params={'arg4': 'value4'})
        input_kwargs = dict(arg2='value2', arg3='value3')
        arg_group.process_request_meta(request_meta, input_kwargs)

        assert 'arg1' not in request_meta


class TestPredefinedArgGroup(object):

    def test_arg_predefine_create_arg(self):
        arg_predefine = arg.ArgPredefine(name='name', default='basic', choices=['basic', 'digest'])
        arg_ = arg_predefine.create_arg()

        assert arg_.name == 'name'
        assert arg_.default == 'basic'
        assert arg_.required is True
        assert arg_.alias is None

    def test_arg_predefine_default_not_in_choices(self):
        with pytest.raises(ValueError):
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

        assert test_group.arg1.raw_dict == {'name': 'arg1',
                                            'required': True,
                                            'default': 'value1',
                                            'alias': None}
        assert test_group.arg2.raw_dict == {'name': 'arg2',
                                            'required': True,
                                            'default': None,
                                            'alias': None}
        assert callback in test_group.arg1._validators
        assert callback in test_group.arg2._validators

    def test_process_request_meta(self):
        class TestGroup(arg.PredefinedArgGroup):
            arg1 = arg.ArgPredefine(default='default')
            arg2 = arg.ArgPredefine()
            arg3 = arg.ArgPredefine(required=False)

        test_group = TestGroup('params', {'arg1': 'value1'})
        request_meta = RequestMeta(params={'arg2': 'current_value2'})
        input_kwargs = dict(arg2='new_value2')

        test_group.process_request_meta(request_meta, input_kwargs)

        assert request_meta['params'] == {'arg1': 'value1',
                                          'arg2': 'new_value2'}

    def test_process_request_meta_input_no_in_choices(self):
        class TestGroup(arg.PredefinedArgGroup):
            arg1 = arg.ArgPredefine(choices=['value1', 'value2'])

        test_group = TestGroup('params')
        request_meta = RequestMeta()
        input_kwargs = dict(arg1='other')

        with pytest.raises(ValueError):
            test_group.process_request_meta(request_meta, input_kwargs)


class TestAuthArgGroup(object):

    def test_create_arg_group(self):
        auth_group = arg.create_group(
            'auth',
            [{'type': 'digest'},
             {'username': {'alias': 'alias_username'}}])

        assert auth_group.type.raw_dict == {'name': 'type',
                                            'default': 'digest',
                                            'required': True,
                                            'alias': None}
        assert auth_group.username.raw_dict == {'name': 'username',
                                                'default': None,
                                                'alias': 'alias_username',
                                                'required': True}
        assert auth_group.password.raw_dict == {'name': 'password',
                                                'default': None,
                                                'alias': None,
                                                'required': True}

    def test_process_request_meta(self):
        auth_group = arg.create_group(
            'auth',
            [{'type': 'digest'}])

        request_meta = RequestMeta(
            auth={'type': 'basic',
                  'username': 'current_username'})
        input_kwargs = dict(username='username', password='password')
        auth_group.process_request_meta(request_meta, input_kwargs)

        assert request_meta['auth'] == {'type': 'digest',
                                        'username': 'username',
                                        'password': 'password'}
