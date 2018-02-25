# -*- coding: utf-8 -*-

from .builder import Api


def jsonify(api):
    def jsonify_hook(resp):
        return resp.json()

    if not isinstance(api, Api):
        raise ValueError('Api instance required')

    api.add_resp_hook(jsonify_hook)

    return api
