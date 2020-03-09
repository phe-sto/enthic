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
from enthic.database.fetch import fetchall
from enthic.utils.not_found_response import NotFoundJSONResponse
from flask import abort


class SQLData:
    """
    Execute a request and store data as attribute. Response 404 if no data retrieved
    """

    def __init__(self, sql_request, args):
        """
        Constructor, execute the and store the result or respond 404.

           :param sql_request: SQL request with data to fetch.
           :param args: SQL argument to pass the request.
        """
        sql_results = fetchall(sql_request, args)
        if sql_results == ():
            abort(NotFoundJSONResponse())
        else:
            self.sql_results = sql_results
