# -*- coding: utf-8 -*-
"""
=========================
Valid JSON response Class
=========================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enthic.utils.json_response import JSONResponse


class OKJSONResponse(JSONResponse):
    """
    Abstraction on top of the Enthic JSONResponse class, as most Response will be
    application/json and HTTP return code 200.
    """

    def __init__(self, object_response):
        """
        Constructor of the OKJSONResponse class.

           :param object_response: Dictionary to convert to JSON.
           :raise TypeError: If argument not a dict, list or tuple.
        """
        if object_response.__class__ is dict \
                or object_response.__class__ is list \
                or object_response.__class__ is tuple:
            JSONResponse.__init__(self, object_response)
        else:
            raise TypeError(
                'OKJSONResponse CLASS CONSTRUCTOR ARGUMENT MUST BE A dict, list or tuple.'
            )
