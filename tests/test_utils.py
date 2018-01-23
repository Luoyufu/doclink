# -*- coding: utf-8 -*-

import unittest

from doclink import utils


class UtilsTestCase(unittest.TestCase):

    def test_NoInput_truth(self):
        self.assertEqual(utils.NoInput or 0, 0)

    def test_raw_arg_from_uri(self):
        raw_args = utils.raw_args_from_uri('/test/{arg1=default1}/{arg2}')

        self.assertEqual(
            raw_args,
            [
                {'arg1': {'default': 'default1'}},
                {'arg2': {'default': None}}
            ])


class ArgNormalizerTestCase(unittest.TestCase):
    single_str_arg = 'single_arg0'
    single_dict_arg = {'single_arg1': 'value'}
    single_dict_arg_with_attr = {
        'single_arg2': {'required': False,
                        'alias': 'alias',
                        'default': 'value'}}

    multi_arg = [
        'multi_arg0',
        {'multi_arg1': 'value'},
        {'multi_arg2': {'required': False,
                        'alias': 'alias',
                        'default': 'value'}}
    ]

    def test_single_str_arg_normalize(self):
        result = utils.ArgNormalizer.normalize(self.single_str_arg)
        self.assertEqual(
            result,
            {'single_arg0': utils.RawArg(**{
                'name': 'single_arg0',
                'default': None,
                'alias': None,
                'required': True})}
        )

    def test_single_dict_arg_normalize(self):
        result = utils.ArgNormalizer.normalize(self.single_dict_arg)
        self.assertEqual(
            result,
            {'single_arg1': utils.RawArg(**{
                'name': 'single_arg1',
                'default': 'value',
                'alias': None,
                'required': True})}
        )

    def test_single_dict_arg_with_atrr(self):
        result = utils.ArgNormalizer.normalize(self.single_dict_arg_with_attr)
        self.assertEqual(
            result,
            {'single_arg2': utils.RawArg(**{
                'name': 'single_arg2',
                'default': 'value',
                'alias': 'alias',
                'required': False})}
        )

    def test_multi_arg(self):
        result = utils.ArgNormalizer.normalize(self.multi_arg)
        self.assertEqual(
            result,
            {
                'multi_arg0': utils.RawArg(**{
                    'name': 'multi_arg0',
                    'default': None,
                    'alias': None,
                    'required': True}),
                'multi_arg1': utils.RawArg(**{
                    'name': 'multi_arg1',
                    'default': 'value',
                    'alias': None,
                    'required': True}),
                'multi_arg2': utils.RawArg(**{
                    'name': 'multi_arg2',
                    'default': 'value',
                    'alias': 'alias',
                    'required': False})
            }
        )
