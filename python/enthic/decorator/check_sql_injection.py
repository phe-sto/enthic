# -*- coding: utf-8 -*-

"""
============================================
Decorator checking SQL injection in requests
============================================
"""
from functools import wraps
from json import loads, JSONDecodeError
from re import compile, IGNORECASE

from flask import request

sql_re = compile(
    'SELECT.*FROM|UPDATE.*SET|INSERT.*INTO|DELETE.*FROM|DROP.*DATABASE|DROP.*TABLE',
    IGNORECASE
)


def check_sql_injection(func):
    """
    Decorator checking SQL injection.
       :param func: Function decorated.
       :return: The function decorated.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper checking SQL injection.
           :param args: Possible arguments.
           :param kwargs: Possible keyword argument.
           :return: The function decorated.
        """
        ########################################################################
        #  CHECK WHEN PARAMETER IS IN PATH
        for parameter in request.view_args.values():
            try:
                if sql_re.match(parameter):
                    raise ValueError("Path parameter cannot be a SQL.")
            except TypeError:  # IF NOT A STRING, ONLY STRING CAN BE AN INJECTION
                continue
        ########################################################################
        #  CHECK WHEN PARAMETER IS IN JSON BODY
        try:
            json_data = loads(request.data)
            if json_data.__class__ is dict:
                for value in json_data.values():
                    try:
                        if sql_re.match(value):
                            raise ValueError("JSON body value cannot be a SQL.")
                    except TypeError:  # IF NOT A STRING, ONLY STRING CAN BE AN INJECTION
                        continue
        except JSONDecodeError:  # IF NOT A JSON
            pass
        return func(*args, **kwargs)

    return wrapper
