# -*- coding: utf-8 -*-
"""
==========================
Flask MySQL initialisation
==========================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from flask_mysqldb import MySQL
from flask import current_app as application
try:
    mysql = MySQL(application)
except RuntimeError:
    pass  # RUNTIME ERROR: WORKING OUTSIDE OF APPLICATION CONTEXT. LIKE EXECUTING SPHINX
