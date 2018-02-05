# -*- coding: utf-8 -*-

import os

from collections import namedtuple

from uritemplate import URITemplate


methods = ("get", "head", "put", "post", "patch", "delete")
RawArg = namedtuple('RawArg', ['name', 'alias', 'required', 'default'])


class _NoInput(object):

    def __bool__(self):
        return False

    # for python 3/2 compatity
    __nonzero__ = __bool__


NoInput = _NoInput()


class ArgNormalizer(object):

    @classmethod
    def _arg_normalize(cls, raw_arg):
        normalized = {
            'name': None,
            'default': None,
            'alias': None,
            'required': True
        }

        if isinstance(raw_arg, dict):
            for name, meta in raw_arg.items():
                normalized.update(name=name)
                if isinstance(meta, dict):
                    normalized.update(cls._parse_meta_dict(meta))
                else:
                    normalized.update(default=meta)
        else:
            normalized.update(name=raw_arg)

        return RawArg(**normalized)

    @classmethod
    def _parse_meta_dict(cls, meta):
        return {
            'required': bool(meta.get('required', True)),
            'default': meta.get('default'),
            'alias': meta.get('alias')
        }

    @classmethod
    def normalize(cls, raw_args):
        if raw_args is None:
            return {}

        raw_arg_list = raw_args if isinstance(raw_args, list) else [raw_args, ]
        raw_arg_map = {}

        for raw_arg in raw_arg_list:
            normalized = cls._arg_normalize(raw_arg)
            raw_arg_map[normalized.name] = normalized

        return raw_arg_map


def raw_args_from_uri(uri):
    uri_template = URITemplate(uri)

    raw_args = []
    for uri_var in uri_template.variables:
        name = uri_var.variable_names[0]
        default = uri_var.defaults.get(name)
        raw_args.append({name: {'default': default}})

    return raw_args


def guess_filename(obj):
    """Tries to guess the filename of the given object."""
    name = getattr(obj, 'name', None)
    if (name and isinstance(name, str) and name[0] != '<' and
            name[-1] != '>'):
        return os.path.basename(name)
