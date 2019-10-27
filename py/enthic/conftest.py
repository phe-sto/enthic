# -*- coding: utf-8 -*-
"""
===========================================
Common Fixtures of the enthic package test.
===========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from json import load

import pytest


@pytest.fixture()
def configuration_path():
    """
    Fixture, path of the configuration path.
       :return: A string of the configuration path.
    """
    return "../configuration.json"


@pytest.fixture()
def python_executable():
    """
    Fixture, path of the python3 executable.
       :return: A string made of the python3 executable path.
    """
    return "../python3_venv/bin/python3"


@pytest.fixture()
def pypy_executable():
    """
    Fixture, path of the pypy3 executable.
       :return: A string made of the pypy3 executable path.
    """
    return "../pypy3.6-v7.1.1-linux64/bin/pypy3"


@pytest.fixture()
def config(configuration_path):
    """
    Fixture of the application configuration.
       :param configuration_path: Fixture, path of the configuration path.
       :return: The configuration object.
    """
    with open(configuration_path) as json_configuration_file:
        return load(json_configuration_file)
