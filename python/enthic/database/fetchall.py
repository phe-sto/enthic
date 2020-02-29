# -*- coding: utf-8 -*-
"""
======================================
Fetchall results on the MySQL database
======================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from flask import current_app as application


def get_results(request):
    """
    Return a fetchall for a given SQL request on the application MySQL database

       :param request: SQL request to execute as a string.
    """
    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        cur.execute(request)
        sql_result = cur.fetchall()
        cur.close()
        return tuple(sql_result)
