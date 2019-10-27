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
def config(configuration_path):
    """
    Fixture of the application configuration.
       :param configuration_path: Fixture, path of the configuration path.
       :return: The configuration object.
    """
    with open(configuration_path) as json_configuration_file:
        return load(json_configuration_file)
