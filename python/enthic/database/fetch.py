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


def get_results(request, sql_func):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
       :param request: Cursor callable attribute to call.
    """
    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        cur.execute(request)
        fetch_func = getattr(cur, sql_func)
        sql_result = fetch_func()
        cur.close()
        return sql_result


def fetchone(request):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
    """
    return get_results(request, "fetchone")[0]


def fetchall(request):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
    """
    return get_results(request, "fetchall")
