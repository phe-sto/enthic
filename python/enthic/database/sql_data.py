# -*- coding: utf-8 -*-
"""
===============
SQL data object
===============

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enthic.database.fetchall import get_results
from enthic.utils.not_found_response import NotFoundJSONResponse
from flask import abort


class SQLData:
    """
    Execute a request and store data as attribute. Response 404 if no data retrieved
    """

    def __init__(self, sql_request):
        """
        Constructor, execute the and store the result or respond 404.

           :param sql_request: SQL request with data to fetch.
        """
        sql_results = get_results(sql_request)
        if sql_request.__len__() > 0:
            self.sql_results = sql_results
        else:
            abort(NotFoundJSONResponse())
