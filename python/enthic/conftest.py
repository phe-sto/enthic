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
from logging import error, info
from subprocess import Popen, TimeoutExpired, PIPE

import pytest


def execution_in_subprocess(python, configuration_path, python_script):
    """
    Execute a command in a subprocess and print both standard and error out.
    Execution with cProfile module to profile python performance.

       :param configuration_path: JSON object of the application configuration.
       :param python: Path to an executable that can run python code.
       :param python_script: Python script to run.
       :return: Return code of the subprocess.
    """
    process = Popen([python, "-m", "cProfile", "-s", "tottime",
                     python_script, "-c", configuration_path], cwd='.',
                    stdout=PIPE, stderr=PIPE)
    try:
        outs, errs = process.communicate(timeout=3600)
    except TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()
    ############################################################################
    # PRINT ONLY IF NOT EMPTY
    if outs != b'':
        info(outs.decode())
    if errs != b'':
        error(errs.decode())
    return process.returncode


@pytest.fixture()
def configuration_path():
    """
    Fixture, path of the configuration path.

       :return: A string of the configuration path.
    """
    return "enthic/configuration.json"


@pytest.fixture()
def python_executable():
    """
    Fixture, path of the python3 executable.

       :return: A string made of the python3 executable path.
    """
    return "python3"


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
