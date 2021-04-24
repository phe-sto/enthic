# -*- coding: utf-8 -*-
"""
=============================
Not found JSON response Class
=============================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from flask import request

from enthic.utils.json_response import JSONResponse


class NotFoundJSONResponse(JSONResponse):
    """
    Abstraction on top of the flask JSON Response class, for not found data JSON,
    application/json and HTTP return code 404. Formatted as hydra JSON-LD.
    """

    def __init__(self):
        """
        Constructor of the NotFoundJSONResponse class.
        """
        JSONResponse.__init__(self, {
            "@context": "http://www.w3.org/ns/hydra/context.jsonld",
            "@type": "Error",
            "@id": request.full_path,
            "title": "Not found",
            "description": "No information found on that company"
        }, status=404)
