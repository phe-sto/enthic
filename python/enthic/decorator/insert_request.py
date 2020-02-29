# -*- coding: utf-8 -*-

"""
=================================================================================
Decorator inserting data from the incoming request after having executed function
=================================================================================
"""
from functools import wraps

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
            try:
                if app_request.__dict__.get('data') and app_request.__dict__['data'] != b'':
                    sql_request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", "%s", CURRENT_TIMESTAMP)""" % \
                                  (app_request.__dict__['environ']['REQUEST_METHOD'],
                                   app_request.__dict__['environ']['PATH_INFO'],
                                   app_request.__dict__['environ']['REMOTE_ADDR'],
                                   app_request.__dict__['environ']['REMOTE_PORT'],
                                   app_request.__dict__['environ']['HTTP_USER_AGENT'],
                                   str(app_request.__dict__['data']).replace('"', "'"))
                elif app_request.__dict__['view_args'] != {}:
                    sql_request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", "%s", CURRENT_TIMESTAMP)""" % \
                                  (app_request.__dict__['environ']['REQUEST_METHOD'],
                                   app_request.__dict__['environ']['PATH_INFO'],
                                   app_request.__dict__['environ']['REMOTE_ADDR'],
                                   app_request.__dict__['environ']['REMOTE_PORT'],
                                   app_request.__dict__['environ']['HTTP_USER_AGENT'],
                                   str(app_request.__dict__['view_args']).replace('"', "'"))
                else:
                    sql_request = """INSERT INTO request VALUES ("%s", "%s", "%s", "%s", "%s", NULL, CURRENT_TIMESTAMP)""" % \
                                  (app_request.__dict__['environ']['REQUEST_METHOD'],
                                   app_request.__dict__['environ']['PATH_INFO'],
                                   app_request.__dict__['environ']['REMOTE_ADDR'],
                                   app_request.__dict__['environ']['REMOTE_PORT'],
                                   app_request.__dict__['environ']['HTTP_USER_AGENT'])
            except KeyError:
                pass
            cur = mysql.connection.cursor()
            cur.execute(sql_request)
            cur.close()
            mysql.connection.commit()

        return handle_request

    return wrapper
