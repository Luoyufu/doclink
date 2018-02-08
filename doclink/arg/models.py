# -*- coding: utf-8 -*-

from six import add_metaclass

from ..exceptions import RequiredArgMissingError
from ..utils import ArgNormalizer, NoInput


def _create_choice_validator(choices):
    def validate(_, value):
        if value not in choices:
            raise ValueError('value:{} not in choices:{}'.
                             format(value, choices))
    return validate


def _required_validator(arg, value):
    if arg.required and value is NoInput:
        raise RequiredArgMissingError(arg.alias or arg.name)


class Arg(object):

    def __init__(self, name, alias=None, required=True, default=None):
        assert name is not None, 'arg name required'
        self.name = name
        self.alias = alias
        self.required = required
        self.default = default
        self._validators = [_required_validator]

    @property
    def raw_dict(self):
        return {
            'name': self.name,
            'alias': self.alias,
            'required': self.required,
            'default': self.default
        }

    @classmethod
    def from_raw(cls, raw_arg):
        """create Arg from RawArg instance
        """
        return cls(
            raw_arg.name,
            raw_arg.alias,
            raw_arg.required,
            raw_arg.default)

    def output(self, current_kwargs, input_kwargs):
        """get the arg value from current_kwargs and input_kwargs

        return:
            key: the key used to get output from input_kwargs
            value: the output
        """
        key = self.alias or self.name
        value = input_kwargs.get(key, NoInput)
        current_value = current_kwargs.get(self.name) if current_kwargs else None

        if value is NoInput:
            maybe_value = self.default if self.default is not None else current_value
            if maybe_value is not None:
                value = maybe_value

        self._validate(value)

        return key, value

    def _validate(self, value):
        for validator in self._validators:
            validator(self, value)

    def add_validator(self, validator):
        """add validator for this arg

        The validator must be a callable with two params(this arg instance and outputed value)
        """
        if not callable(validator):
            raise ValueError('validator must be callable')

        self._validators.append(validator)


class ArgGroup(object):
    """docstring for Arg"""

    def __init__(self, group_name, raw_args=None, validators=None,
                 arg_cls=Arg, normalizer=ArgNormalizer):
        self.group_name = group_name
        self.arg_cls = arg_cls
        self.raw_arg_map = normalizer.normalize(raw_args)
        self.validators = validators
        self.arg_map = None
        self._build_arg_map()

    def _build_arg_map(self):
        arg_map = {}

        for arg_name, raw_arg in self.raw_arg_map.items():
            arg = self.arg_cls.from_raw(raw_arg)

            if self.validators:
                validator = self.validators.get(arg_name)
                if validator:
                    arg.add_validator(validator)

            arg_map[arg_name] = arg

        self.arg_map = arg_map

    def _get_arg_result(self, current_kwargs, input_kwargs):
        result = {}
        used_arg_set = set()
        for arg in self.arg_map.values():
            key, output = arg.output(current_kwargs, input_kwargs)
            if output is not NoInput:
                result[arg.name] = output
                used_arg_set.add(key)

        return used_arg_set, result

    def _update_request_meta(self, request_meta, arg_result):
        # if all the args are not required, and no input values for them,
        # the arg_result will be an empty dict
        if arg_result:
            param = request_meta.setdefault(self.group_name, {})
            param.update(arg_result)

    def process_request_meta(self, request_meta, input_kwargs):
        current_kwargs = request_meta.get(self.group_name)
        used_arg_set, arg_result = self._get_arg_result(current_kwargs, input_kwargs)
        self._update_request_meta(request_meta, arg_result)

        return used_arg_set


class ArgPredefine(object):
    """Descriptor for arg predefinition.

    set it with Arg instance.
    It can create an arg if the arg is not defined in pydoc.
    """

    def __init__(self, arg_cls=Arg, arg_validator=None, choices=None,
                 **default_attrs):
        self.default_attrs = default_attrs

        if arg_validator:
            assert callable(arg_validator), 'validator must be callable'

        default = self.default_attrs.get('default')
        if not (default is None or choices is None):
            if default not in choices:
                raise ValueError('default:{} not in choices:{}'.format(default, choices))

        self.name = None
        self.arg_cls = arg_cls
        self.arg_validator = arg_validator
        self.choices = choices

    def create_arg(self):
        return self.arg_cls(self.name, **self.default_attrs)

    def __get__(self, instance, owner):
        return instance.arg_map[self.name]

    def __set__(self, instance, arg):
        if not isinstance(arg, self.arg_cls):
            raise ValueError('{} instacne required: {}'.format(
                self.arg_cls.__name__, type(arg).__name__))
        if self.storage_name is None:
            raise RuntimeError('set Arg before storage_name determined')

        if self.choices:
            validator = _create_choice_validator(self.choices)
            if arg.default is not None:
                validator(arg, arg.default)

            arg.add_validator(validator)

        if self.arg_validator:
            arg.add_validator(self.arg_validator)

        instance.arg_map[self.name] = arg


class PredefinedArgGroupMeta(type):
    """metaclass for predefined argGroup.

    It helps build ArgPredefine descriptor:
        set arg name, set storage_name and create arg_predefines list
    """

    def __init__(cls, name, bases, attr_dict):
        super(PredefinedArgGroupMeta, cls).__init__(name, bases, attr_dict)
        arg_predefines = []
        for key, attr in attr_dict.items():
            if isinstance(attr, ArgPredefine):
                attr.name = key
                attr.storage_name = '{}@{}'.format(key, name)
                arg_predefines.append(attr)

        cls.arg_predefines = arg_predefines


@add_metaclass(PredefinedArgGroupMeta)
class PredefinedArgGroup(ArgGroup):

    def _build_arg_map(self):
        self.arg_map = {}

        for arg_predefine in self.arg_predefines:
            arg_name = arg_predefine.name
            if arg_name in self.raw_arg_map:
                arg = self.arg_cls.from_raw(self.raw_arg_map[arg_name])
            else:
                arg = arg_predefine.create_arg()

            if self.validators:
                validator = self.validators.get(arg_name)
                if validator:
                    arg.add_validator(validator)

            setattr(self, arg_name, arg)
