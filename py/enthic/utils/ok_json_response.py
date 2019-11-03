# -*- coding: utf-8 -*-
from json import dumps

from flask import Response


class OKJSONResponse(Response):
    """
    Abstraction on top of the flask Response class, as most Response will be
       application/json and HTTP return code 200.
    """

    def __init__(self, object_response):
        """
        Constructor of the OKJSONResponse class.
           :param object_response: Dictionary to convert to JSON.
           :raise TypeError: If argument not a dict.
        """
        if object_response.__class__ is dict \
                or object_response.__class__ is list \
                or object_response.__class__ is tuple:
            Response.__init__(self, dumps(object_response),
                              status=200, mimetype='application/json'
                              )
        else:
            raise TypeError(
                'OKJSONResponse CLASS CONSTRUCTOR ARGUMENT MUST BE AN dict.'
            )
