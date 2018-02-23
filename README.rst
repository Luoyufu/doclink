*******
Doclink
*******

.. image:: https://travis-ci.org/Luoyufu/doclink.svg?branch=master
    :target: https://travis-ci.org/Luoyufu/doclink

.. image:: https://codecov.io/gh/Luoyufu/doclink/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/Luoyufu/doclink

.. image:: https://img.shields.io/pypi/v/doclink.svg
  :target: https://pypi.python.org/pypi/doclink

.. image:: https://img.shields.io/pypi/pyversions/doclink.svg
  :target: https://pypi.python.org/pypi/doclink

| Build client for Web APIs from pydoc. Inspired by `Uplink <https://github.com/prkumar/uplink>`_.

Overview
========
| Doclink turns a Python function into HTTP API by writting pydoc to declare the api meta.
| It is based on Requests and uses YAML with predefined schema as api declaration.
| When calling the function, response from HTTP API will be passed in as a parameter for futher handling.

Features
========
* create python function as HTTP API with **pydoc**
* **YAML** based schema for api declaration
* handle api response in the **same** function
* response hook as **middleware**
* **all** args for Requests supported
* select base_uri dynamicly from simple **router**

Quick through, with httpbin
=====
Create a consumer instance.

.. code-block:: python

    from doclink import Consumer

    consumer = Consumer('http://httpbin.org/')

Add response hook(middleware).

.. code-block:: python

    @consumer.resp_hook
    def json_hook(resp):
        resp.json = resp.json()

Add function for api declaration.

.. code-block:: python

        @consumer.get('get')
        def get(resp):
            """
            <meta>
                args:
                    query:
                        - arg1: arg1
                        - arg2: arg2
            </meta>
            """
            return resp.json['args']

Use you api.

.. code-block:: python

    >>> get()
    {
        "arg1": "arg1",
        "arg2": "arg2"
    }
