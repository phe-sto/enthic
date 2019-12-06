# -*- coding: utf-8 -*-
"""
=============================================
Test the sum of bundle codes from sorted file
=============================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

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
    assert config['outputPath'].__class__ is str, "OUTPUT PATH CONF NOT A STRING"
    assert config['sortBundleFile'].__class__ is str, "SORTED RESULT FILENAME CONF NOT A STRING"


################################################################################
# EXECUTION, IN CPYTHON 3 AND PYPY VM
@pytest.fixture()
def sum_bundle_script():
    """
    Fixture of the Python script that sum bundle for a year and a company.

       :return: A string made of the script path.
    """
    return "./enthic/sum_bundle.py"


def test_execution_python(configuration_path, python_executable,
                          sum_bundle_script):
    """
    Test the execution with the CPython 3 implementation.

       :param configuration_path: Fixture of the application configuration.
       :param python_executable: Fixture, path of the python3 executable.
    """
    rc = execution_in_subprocess(python_executable, configuration_path,
                                 sum_bundle_script)
    assert rc == 0, "RETURN CODE NOT 0"


@pytest.mark.skip
def test_execution_pypy(configuration_path, pypy_executable,
                        sum_bundle_script):
    """
    Test the execution with the Pypy VM 3 implementation.

       :param configuration_path: Fixture of the application configuration.
       :param pypy_executable: Fixture, path of the pypy3 executable..
    """
    rc = execution_in_subprocess(pypy_executable, configuration_path,
                                 sum_bundle_script)
    assert rc == 0, "RETURN CODE NOT 0"
