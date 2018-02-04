# -*- coding: utf-8 -*-

from .models import ArgGroup
from .models import PredefinedArgGroup
from .models import ArgPredefine

_arg_group_map = {}
common_arg_group_names = (
    'params',
    'headers',
    'json',
    'data',
    'params',
    'cookies',
    'files',
    'path',
    'multipart')


def register_arg_group(group_name):
    def deco(cls):
        assert issubclass(cls, ArgGroup), 'cannot register non-ArgGroup cls'
        _arg_group_map[group_name] = cls
        return cls
    return deco


def unregister_arg_group(group_name):
    try:
        del _arg_group_map[group_name]
    except KeyError:
        pass


@register_arg_group('auth')
class AuthArgGroup(PredefinedArgGroup):
    type = ArgPredefine(default='basic', choices=['basic', 'digest'])
    username = ArgPredefine()
    password = ArgPredefine()


for group_name in common_arg_group_names:
    register_arg_group(group_name)(ArgGroup)


def create_group(group_name, raw_args, validators=None):
    try:
        return _arg_group_map[group_name](group_name, raw_args, validators)
    except KeyError:
        raise ValueError('group_name:{} unknown'.format(group_name))
