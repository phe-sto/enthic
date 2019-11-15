# -*- coding: utf-8 -*-
from json import dumps

from flask import Response


class JSONResponse(Response):
    """
    Abstraction on top of the flask Response class, as most Response will be
       application/json and HTTP default return code 200, but can be changed.
    """

    def __init__(self, object_response, status=200):
        """
        Constructor of the OKJSONResponse class.
           :param object_response: Dictionary to convert to JSON.
           :param status: Default is 200.
           :raise TypeError: If argument not a dict, list or tuple.
        """
        if object_response.__class__ is dict \
                or object_response.__class__ is list \
                or object_response.__class__ is tuple:
            Response.__init__(self, dumps(object_response),
                              status=status, mimetype='application/json'
                              )
        else:
            raise TypeError(
                'OKJSONResponse CLASS CONSTRUCTOR ARGUMENT MUST BE A dict, list or tuple.'
            )
