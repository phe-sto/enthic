# -*- coding: utf-8 -*-
"""
========================================
========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from os.path import dirname, join, basename, abspath, pardir, getsize
import os
from glob import glob
import subprocess
from argparse import ArgumentParser
from io import BytesIO
import sys
from json import load
from ftplib import FTP_TLS
import shutil
import urllib
import wget
from py7zr import SevenZipFile
from logging import info, error

from sqlalchemy import create_engine, Column, Integer, String, Date, Float

from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Bundle(Base):

    __tablename__ = 'bundle'

    siren = Column(type_=Integer, nullable=False, primary_key=True)
    declaration = Column(type_=Integer, nullable=False, primary_key=True)
    accountability = Column(type_=Integer, nullable=False, primary_key=True)
    bundle = Column(type_=Integer, nullable=False, primary_key=True)
    amount = Column(type_=Float, nullable=False)
