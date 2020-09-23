# -*- coding: utf-8 -*-

"""
=================================================================================
Decorator inserting data from the incoming request after having executed function
=================================================================================
"""
from functools import wraps

from MySQLdb._exceptions import DataError
from flask import current_app as application, request as app_request


def insert_request(func):
    """
    Decorator inserting relevant request data timestamped.

       :param func: Function decorated.
       :return: The function decorated.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper to the insert in another thread to save time.

           :param args: Possible arguments.
           :param kwargs: Possible keyword argument.
           :return: The function decorated.
        """
        handle_request = func(*args, **kwargs)
        with application.app_context():
            from enthic.database.mysql import mysql
            if app_request.__dict__.get('data') and app_request.__dict__['data'] != b'':
                sql_request = 'INSERT INTO request VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
                args = (str(app_request.__dict__['data']),)
            elif app_request.__dict__['view_args'] != {}:
                sql_request = 'INSERT INTO request VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
                args = (str(app_request.__dict__['view_args']),)
            else:
                sql_request = 'INSERT INTO request VALUES (%s, %s, NULL, CURRENT_TIMESTAMP)'
                args = tuple()
            cur = mysql.connection.cursor()
            if app_request.__dict__['environ'].get('PATH_INFO') \
                    and app_request.__dict__['environ'].get('PATH_INFO') != b'':
                uri = app_request.__dict__['environ']['PATH_INFO']
            else:
                uri = "UNKNOWN URI"
            if app_request.__dict__['environ'].get('HTTP_USER_AGENT') \
                    and app_request.__dict__['environ'].get('HTTP_USER_AGENT') != b'':
                agent = app_request.__dict__['environ']['HTTP_USER_AGENT']
            elif app_request.__dict__['environ'].get('HTTP_HTTP_USER_AGENT') \
                    and app_request.__dict__['environ'].get('HTTP_HTTP_USER_AGENT') != b'':
                agent = app_request.__dict__['environ']['HTTP_HTTP_USER_AGENT']
            else:
                agent = "UNKNOWN AGENT"
            try:
                cur.execute(sql_request, (*(uri, agent), *args))
            except DataError:
                pass
            finally:
                cur.close()
                mysql.connection.commit()

        return handle_request

    return wrapper
