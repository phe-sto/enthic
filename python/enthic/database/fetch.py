# -*- coding: utf-8 -*-
"""
===================================
Fetch results on the MySQL database
===================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from flask import current_app as application


def get_results(request, args, sql_func):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
       :param args: SQL argument to pass the request.
       :param request: Cursor callable attribute to call.
    """
    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        cur.execute(request, args)
        fetch_func = getattr(cur, sql_func)
        sql_result = fetch_func()
        cur.close()
        return sql_result


def fetchone(request, args=None):
    """
    Return a fetchone for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
       :param args: SQL argument to pass the request. Default is None.
    """
    return get_results(request, args, "fetchone")


def fetchall(request, args=None):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
       :param args: SQL argument to pass the request. Default is None.
    """
    return get_results(request, args, "fetchall")
