# -*- coding: utf-8 -*-

from doclink.clients.requests_ import RequestsClient


class FakeRequestMeta(dict):

    def get_url(self):
        return 'http://fake_url'


class FakeSession(object):

    def request(self, **kwargs):
        return 'ok'


class TestCreateFilesArg(object):

    def test_with_file_path(self):
        client = RequestsClient()
        file_path = 'tox.ini'

        request_meta = {'files': {'field': file_path}}
        result = client._create_files_arg(request_meta['files'])

        with open(file_path, 'rb') as f:
            result_f = result['field']

            assert result_f.name == f.name
            assert type(result_f) == type(f)

    def test_with_file_object(self):
        client = RequestsClient()
        file_path = 'tox.ini'

        with open(file_path, 'rb') as f:
            request_meta = {'files': {'field': f}}
            result = client._create_files_arg(request_meta['files'])

            assert result == {'field': f}

    def test_with_str(self):
        client = RequestsClient()
        str_arg = 'test.ini'

        request_meta = {'files': {'field': str_arg}}
        result = client._create_files_arg(request_meta['files'])

        assert result == {'field': str_arg}

    def test_with_file_read(self):
        client = RequestsClient()
        file_path = 'tox.ini'

        with open(file_path, 'rb') as f:
            file_read = f.read()
            request_meta = {'files': {'field': file_read}}
            result = client._create_files_arg(request_meta['files'])

            assert result == {'field': file_read}

    def test_with_tuple(self):
        client = RequestsClient()
        str_arg = 'test.ini'

        request_meta = {'files': {'field': ('filename', str_arg)}}
        result = client._create_files_arg(request_meta['files'])

        assert result == {'field': ('filename', str_arg)}


class TestCreateMultipartArg(object):

    def test_with_file_path(self):
        client = RequestsClient()
        file_path = 'tox.ini'

        request_meta = {'multipart': {'field': file_path}}
        result = client._create_multipart_arg(request_meta['multipart'])

        with open(file_path, 'rb') as f:
            result_value = result['field']
            result_file_name = result_value[0]
            result_file_obj = result_value[1]

            assert isinstance(result_value, tuple)
            assert len(result_value) == 2
            assert result_file_name == 'tox.ini'
            assert type(result_file_obj) == type(f)

    def test_with_file_object(self):
        client = RequestsClient()
        file_path = 'tox.ini'

        with open(file_path, 'rb') as f:
            request_meta = {'multipart': {'field': f}}
            result = client._create_multipart_arg(request_meta['multipart'])

            assert result == {'field': ('tox.ini', f)}

    def test_with_tuple(self):
        client = RequestsClient()
        str_arg = 'test.ini'

        request_meta = {'multipart': {'field': ('filename', str_arg)}}
        result = client._create_multipart_arg(request_meta['multipart'])

        assert result == {'field': ('filename', str_arg)}


class TestRequestsClient(object):

    def test_get_sending_kwargs(self):
        client = RequestsClient()
        request_meta = FakeRequestMeta({
            'method': 'get',
            'params': {
                'param_arg1': 'param_value1',
                'param_arg2': 'param_value2'},
            'unknown': 'unknown'})

        kwargs = client._get_sending_kwargs(request_meta)

        assert kwargs == {
            'method': 'get',
            'url': 'http://fake_url',
            'params': {
                'param_arg1': 'param_value1',
                'param_arg2': 'param_value2'},
        }

    def test_request(self):
        client = RequestsClient(FakeSession())
        request_meta = FakeRequestMeta({
            'method': 'get',
            'params': {
                'param_arg1': 'param_value1',
                'param_arg2': 'param_value2'},
            'unknown': 'unknown'})

        assert client.request(request_meta) == 'ok'
