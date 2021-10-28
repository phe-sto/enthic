# -*- coding: utf-8 -*-
"""
========================================
Test the data extracted from bundle code
========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from logging import info
from os.path import join

import pytest
from enthic.conftest import execution_in_subprocess


################################################################################
# CONFIGURATION
def test_config(config):
    """
    Test the configuration file.

        :param config: Fixture of the JSON configuration file.
    """
    assert config.__class__ is dict, "CONFIGURATION NOT A VALID DICTIONARY"
    assert config['inputPath'].__class__ is str, "INPUT PATH CONF NOT A STRING"
    assert config['accountOntologyCSV'].__class__ is str, "ONTOLOGY FILENAME CONF NOT A STRING"
    assert config["debugLevel"].__class__ is str, "DEBUG LEVEL NOT A STRING"


################################################################################
# EXECUTION, IN CPYTHON 3 AND PYPY VM
@pytest.fixture()
def extract_bundle_script():
    """
    Fixture of the Python script extracting bundle.

       :return: A string made of the script path.
    """
    return "./enthic/scraping/extract_bundle.py"


def test_execution_python(configuration_path, python_executable,
                          extract_bundle_script):
    """
    Test the execution with the CPython 3 implementation.

       :param configuration_path: Fixture of the application configuration.
       :param python_executable: Fixture, path of the python3 executable.
    """
    rc = execution_in_subprocess(python_executable, configuration_path,
                                 extract_bundle_script)
    assert rc == 0, "RETURN CODE NOT 0"


@pytest.mark.skip
def test_execution_pypy(configuration_path, pypy_executable,
                        extract_bundle_script):
    """
    Test the execution with the Pypy VM 3 implementation.

       :param configuration_path: Fixture of the application configuration.
       :param pypy_executable: Fixture, path of the pypy3 executable..
    """
    rc = execution_in_subprocess(pypy_executable, configuration_path,
                                 extract_bundle_script)
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
    return open(join(config['outputPath'], config['tmpBundleFile']), "r")


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
    Test the line contain always 6 columns (with line separator). Check it's
    type.

       :param result_file: Fixture of the CSV result file.
    """
    for line in result_file:
        line = line.split("\t")
        assert len(line) == 6, "NUMBER OF COLUMNS NOT 6"
        assert " " not in line, "BLANK ENTRY"
        assert "" not in line, "EMPTY ENTRY"
        assert line[0].isnumeric() is True, "SIREN NOT NUMERIC"
        assert int(line[0]) < 1000000000, " NOT < 1 000 000 000"
        assert len(line[0]) <= 9, "SIREN IS NOT 9 CHARACTERS"
        assert line[1].isnumeric() is True, "YEAR NOT NUMERIC"
        assert len(line[1]) == 4, "YEAR IS NOT 4 CHARACTERS"
        assert int(line[3]) != 0, "BUNDLE AMOUNT NOT NUMERIC"
        assert int(line[3]) - float(line[3]) == 0, "BUNDLE AMOUNT NOT A FLOAT"


def test_identity_line_data(identity_file):
    """
    Test the line contain always 6 columns (with line separator). Check it's type.

       :param identity_file: Fixture of the CSV result file.
    """
    max_length = 0
    for line in identity_file:
        line = line.split("\t")
        assert len(line) == 6, "NUMBER OF COLUMNS NOT 6"
        assert " " not in line, "BLANK ENTRY"
        assert "" not in line, "EMPTY ENTRY"
        assert line[0].isnumeric() is True, "SIREN NOT NUMERIC"
        assert int(line[0]) < 1000000000, " NOT < 1 000 000 000"
        assert line[2].isnumeric(), "APE IS NOT NUMERIC"
        assert line[3].isnumeric() is True or line[3] == "UNKNOWN", "POSTAL CODE NOT NUMERIC"
        assert len(line[2]) <= 5 or line[2
        ] == "UNKNOWN", "POSTAL CODE NOT 5 CHARACTERS"
        # DENOMINATION LENGTH
        denomination_length = len(line[1])
        if max_length < denomination_length:
            max_length = denomination_length
        info("> MAXIMUM DENOMINATION LENGTH >{}<".format(max_length))
