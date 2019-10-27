# -*- coding: utf-8 -*-
"""
========================================
Test the data extracted form bundle code
========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from logging import error, info
from os.path import join
from subprocess import Popen, TimeoutExpired, PIPE

import pytest


################################################################################
# CONFIGURATION
def test_config(config):
    """
    Test the configuration file.
        :param config: Fixture of the JSON configuration file.
    """
    assert config.__class__ is dict, "CONFIGURATION NOT A VALID DICTIONARY"
    assert config['inputPath'].__class__ is str, "INPUT PATH CONF NOT A STRING"
    assert config['outputPath'].__class__ is str, "OUTPUT PATH CONF NOT A STRING"
    assert config['bundleFile'].__class__ is str, "RESULT FILENAME CONF NOT A STRING"
    assert config['identityFile'].__class__ is str, "IDENTITY FILENAME CONF NOT A STRING"
    assert config['accountOntologyCSV'].__class__ is str, "ONTOLOGY FILENAME CONF NOT A STRING"
    assert config["debugLevel"].__class__ is str, "DEBUG LEVEL NOT A STRING"


################################################################################
# EXECUTION, IN CPYTHON 3 AND PYPY VM
def execution_in_subprocess(python, configuration_path):
    """
    Execute a command in a subprocess and print both standard and error out.
       Execution with cProfile module to profile python performance.
       :param configuration_path: JSON object of the application configuration.
       :param python: Path to an executable that can run python code.
       :return: Return code of the subprocess.
    """
    process = Popen([python, "-m", "cProfile", "-s", "tottime",
                     "./enthic/extract_bundle.py", "-c",
                     configuration_path], cwd='.', stdout=PIPE, stderr=PIPE)
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


def test_execution_python(configuration_path, python_executable):
    """
    Test the execution with the CPython 3 implementation.
       :param configuration_path: Fixture of the application configuration.
       :param python_executable: Fixture, path of the python3 executable.
    """
    rc = execution_in_subprocess(python_executable, configuration_path)
    assert rc == 0, "RETURN CODE NOT 0"


def test_execution_pypy(configuration_path, pypy_executable):
    """
    Test the execution with the Pypy VM 3 implementation.
       :param configuration_path: Fixture of the application configuration.
       :param pypy_executable: Fixture, path of the pypy3 executable..
    """
    rc = execution_in_subprocess(pypy_executable, configuration_path)
    assert rc == 0, "RETURN CODE NOT 0"


################################################################################
# OUTPUT DATA FILES
@pytest.fixture()
def result_file(config):
    """
    Fixture of the CSV result file.
       :param config: Fixture of the JSON configuration file.
       :return: The file object.
    """
    return open(join(config['outputPath'], config['bundleFile']), "r")


@pytest.fixture()
def identity_file(config):
    """
    Fixture of the CSV identity file.
       :param config: Fixture of the JSON configuration file.
       :return: The file object.
    """
    return open(join(config['outputPath'], config['identityFile']), "r")


def test_result_line_data(result_file):
    """
    Test the line contain always 4 columns. Check it's type.
       :param result_file: Fixture of the CSV result file.
    """
    for line in result_file:
        line = line.split(";")
        assert len(line) == 5, "NUMBER OF COLUMNS NOT 5"
        assert " " not in line, "BLANK ENTRY"
        assert "" not in line, "EMPTY ENTRY"
        assert line[0].isnumeric() is True, "SIREN NOT NUMERIC"
        assert len(line[0]) == 9, "SIREN IS NOT 9 CHARACTERS"
        assert line[1].isnumeric(), "YEAR NOT NUMERIC"
        assert len(line[1]) == 4, "YEAR IS NOT 4 CHARACTERS"
        assert int(line[3]) != 0, "BUNDLE AMOUNT NOT NUMERIC"


def test_identity_line_data(identity_file):
    """
    Test the line contain always 4 columns. Check it's type.
       :param identity_file: Fixture of the CSV result file.
    """
    for line in identity_file:
        line = line.split(";")
        assert len(line) == 5, "NUMBER OF COLUMNS NOT 5"
        assert " " not in line, "BLANK ENTRY"
        assert "" not in line, "EMPTY ENTRY"
        assert line[0].isnumeric() is True, "SIREN NOT NUMERIC"
        assert len([2]) == 1, "ACCOUNTABILITY TYPE LENGTH NOT 5"
        assert line[3] == "EUR", "DEVISE NOT EUR"
