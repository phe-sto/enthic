# -*- coding: utf-8 -*-
"""
=========================
Error JSON response Class
=========================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enthic.utils.json_response import JSONResponse
from flask import request


class ErrorJSONResponse(JSONResponse):
    """
    Abstraction on top of the flask JSON Response class, for error JSON,
    application/json and HTTP return code 400. Formatted as hydra JSON-LD.
    """

    def __init__(self, error_message):
        """
        Constructor of the ErrorJSONResponse class.

           :param error_message: Error message to return in dictionary.
           :raise TypeError: If argument not a str.
        """
        if error_message.__class__ is str:
            JSONResponse.__init__(self, {
                "@context": "http://www.w3.org/ns/hydra/context.jsonld",
                "@type": "Error",
                "@id": request.full_path,
                "title": "Bad request",
                "description": error_message
            }, status=400)
        else:
            raise TypeError(
                'ErrorJSONResponse CLASS CONSTRUCTOR ARGUMENT MUST BE AN str.'
            )
