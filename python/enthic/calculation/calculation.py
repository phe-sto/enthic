# -*- coding: utf-8 -*-
"""
==========================
Enum of bundle calculation
==========================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enum import Enum


class BundleCalculation(Enum):
    """
    Classification of type of bundle calculation to return. Their name and value
    should be self explanatory:

    - ALL
    - AVERAGE
    """
    ALL = "ALL"
    AVERAGE = "AVERAGE"
