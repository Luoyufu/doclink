# -*- coding: utf-8 -*-

import atexit
import os

import requests
from requests_toolbelt import MultipartEncoder
from six import string_types


class RequestsClient(object):

    optional_args = (
        'params', 'data', 'headers', 'cookies', 'files',
        'auth', 'timeout', 'allow_redirects', 'proxies',
        'hooks', 'stream', 'verify', 'cert', 'json',
        'multipart')

    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
            atexit.register(session.close)
        self._session = session

    @classmethod
    def _prepare_optional_args(cls, sending_kwargs, request_meta):
        for arg in cls.optional_args:
            value = request_meta.get(arg)
            if value is not None:
                if arg == 'auth':
                    sending_kwargs['auth'] = cls._create_auth_arg(value)
                elif arg == 'files':
                    files_arg = cls._create_files_arg(value)
                    if files_arg:
                        sending_kwargs['files'] = files_arg
                elif arg == 'multipart':
                    multipart_arg = cls._create_multipart_arg(value)
                    if multipart_arg:
                        encoder = MultipartEncoder(multipart_arg)
                        sending_kwargs['data'] = encoder
                        headers = sending_kwargs.setdefault('headers', {})
                        headers['Content-Type'] = encoder.content_type
                else:
                    sending_kwargs[arg] = value

    @classmethod
    def _get_sending_kwargs(cls, request_meta):
        sending_kwargs = {}
        sending_kwargs.update(
            method=request_meta['method'],
            url=request_meta.get_url(),
        )
        cls._prepare_optional_args(sending_kwargs, request_meta)

        return sending_kwargs

    @classmethod
    def _create_files_arg(cls, files_meta):
        """Create files arg for requests.

        Args:
            files_meta (dict): Countain filed name and file_info mapping.

        Returns:
            A dict mapping field name to file_item for multipart/form-data
        """
        def create_file_item(file_info):
            """Nested function to create a file item for files arg.

            Args:
                File_info: If it's a file_path str, open it as file_object.
                    Else, pass it to requests files arg.

            Returns:
                File instance or file_info tuple. For example:

                    open('report.xls', 'rb')
                    ('report.xls', open('report.xls', 'rb'))
            """

            if isinstance(file_info, string_types):
                try:
                    return open(file_info, 'rb')  # param is file_path
                except (IOError, TypeError):
                    pass

            return file_info

        files_arg = {}

        for field, file_infos in files_meta.items():
            if isinstance(file_infos, list):
                files_arg[field] = [create_file_item(file_info) for file_info in file_infos]
            else:
                files_arg[field] = create_file_item(file_infos)

        return files_arg

    @classmethod
    def _create_auth_arg(cls, auth_meta):
        if auth_meta['type'] == 'basic':
            return requests.auth.HTTPBasicAuth(auth_meta['username'], auth_meta['password'])
        else:
            return requests.auth.HTTPDigestAuth(auth_meta['username'], auth_meta['password'])

    @classmethod
    def _create_multipart_arg(cls, multipart_meta):
        """Create a MultipartEncoder instance for multipart/form-data.

        Requests_toolbelt will not try to guess file_name. To encode a file we need
        to give file_name explicitly.

        Args:
            multipart_meta (dict): Map field name to multipart form-data value.
        """

        def create_multipart_item(item_info):
            """Nested function to create a multipart item for files arg.

            Args:
                item_info: If it's a file_path str, open it as file_object as set file_name.
                    Else, pass it to requests_toolbelt MultipartEncoder.

            Returns:
                File instance or file_info tuple. For example:

                    ('report.xls', open('report.xls', 'rb'))
            """
            if isinstance(item_info, string_types):
                try:
                    return (os.path.basename(item_info), open(item_info, 'rb'))  # file_path
                except (IOError, TypeError):
                    pass

            try:
                return (os.path.basename(item_info.name), item_info)  # file_object
            except AttributeError:
                pass

            return item_info

        multipart_arg = {}

        for field, item_infos in multipart_meta.items():
            if isinstance(item_infos, list):
                multipart_arg[field] = [create_multipart_item(item_info)
                                        for item_info in item_infos]
            else:
                multipart_arg[field] = create_multipart_item(item_infos)

        return multipart_arg

    def request(self, request_meta):
        sending_kwargs = self._get_sending_kwargs(request_meta)
        return self._session.request(**sending_kwargs)
