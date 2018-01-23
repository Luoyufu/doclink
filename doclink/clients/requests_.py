# -*- coding: utf-8 -*-

import atexit

import requests


class RequestsClient(object):

    optional_args = (
        'params', 'data', 'headers', 'cookies', 'files',
        'auth', 'timeout', 'allow_redirects', 'proxies',
        'hooks', 'stream', 'verify', 'cert', 'json')

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
                    sending_kwargs['files'] = cls._create_files_arg(value)
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
    def _create_file_item(self, file_info):
        """Create a file item for files arg.

        Args:
            File_info (str/tuple/file-like obj): file_path str, file_info tuple or file-like obj.
            For example:
                'file_path.avi'
                open('file_path.avi')
                {file_name, open('file_path.avi'), 'application/vnd.ms-excel'}
                {file_name, open('file_path.avi').read()}

        Returns:
            File instance or file_info tuple.
            For example:
                 open('report.xls', 'rb')
                 ('report.xls', open('report.xls', 'rb'))
        """
        if isinstance(file_info, str):
            try:
                return open(file_info, 'rb')
            except (IOError, TypeError):
                return file_info
        else:
            return file_info

    @classmethod
    def _create_files_arg(self, files_meta):
        files_arg = {}

        for field, file_infos in files_meta.items():
            if isinstance(file_infos, list):
                files_arg[field] = [self._create_file_item(file_info) for file_info in file_infos]
            else:
                files_arg[field] = self._create_file_item(file_infos)

        return files_arg

    @classmethod
    def _create_auth_arg(self, auth_meta):
        if auth_meta['type'] == 'basic':
            return requests.auth.HTTPBasicAuth(auth_meta['username'], auth_meta['password'])
        else:
            return requests.auth.HTTPDigestAuth(auth_meta['username'], auth_meta['password'])

    def request(self, request_meta):
        sending_kwargs = self._get_sending_kwargs(request_meta)
        return self._session.request(**sending_kwargs)
