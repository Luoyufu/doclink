# -*- coding: utf-8 -*-


class DoclinkError(Exception):
    pass


class MetaParserUnknownError(DoclinkError):
    def __init__(self, name, msg=None):
        msg = msg or 'unknown meta parser: {}'.format(name)
        super(MetaParserUnknownError, self).__init__(msg)


class RequiredArgMissingError(DoclinkError):
    def __init__(self, arg_name, msg=None):
        msg = msg or 'required arg missing: {}'.format(arg_name)
        super(RequiredArgMissingError, self).__init__(msg)


class StatusCodeUnexpectedError(DoclinkError):
    def __init__(self, expected, status_code, resp, msg=None):
        self.status_code = status_code
        self.resp = resp
        msg = msg or 'status:{}, expected:{}'.format(status_code, expected)
        super(StatusCodeUnexpectedError, self).__init__(msg)


class ApimetaNotFoundError(DoclinkError):
    def __init__(self, msg=None):
        msg = msg or 'api meta not found in pydoc'
        super(ApimetaNotFoundError, self).__init__(msg)


class InvalidApimetaItemError(DoclinkError):
    def __init__(self, event, msg=None):
        msg = msg or 'Invalid Apimeta item:{}'.format(event)
        super(InvalidApimetaItemError, self).__init__(msg)
