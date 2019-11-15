# -*- coding: utf-8 -*-

from enthic.utils.json_response import JSONResponse


class ErrorJSONResponse(JSONResponse):
    """
    Abstraction on top of the flask JSON Response class, for error JSON,
       application/json and HTTP return code 400.
    """

    def __init__(self, error_message):
        """
        Constructor of the OKJSONResponse class.
           :param error_message: Error message to return in dictionary.
           :raise TypeError: If argument not a str.
        """
        if error_message.__class__ is str:
            JSONResponse.__init__(self, {"error": error_message}, status=400)
        else:
            raise TypeError(
                'ErrorJSONResponse CLASS CONSTRUCTOR ARGUMENT MUST BE AN str.'
            )
