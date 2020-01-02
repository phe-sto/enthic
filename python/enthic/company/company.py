# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
============================
Class representing a company
============================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from enthic.utils.ok_json_response import OKJSONResponse


class Company(OKJSONResponse):
    """
    Company class inherit from OKJSONResponse.
    """
    def __int__(self, sql_results):
        """
        Constructor of the Company class. Attribute defined based on SQL results.

           :param sql_results: Result from a previously executed request.
        """
        self.siren = sql_results[0][0]
        self.denomination = sql_results[0][1]
        self.accountability = sql_results[0][2]
        self.devise = sql_results[0][3]
        for line in sql_results:
            setattr(self, line[4], line[5])
        OKJSONResponse.__init__(self, self.dict)
