# -*- coding: utf-8 -*-
"""
=============================
Enum of divers classification
=============================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enum import Enum


class Classification(Enum):
    """
    Classification of company by my subjective judgement. The goal is to provide
    IHM UX/UI a generic indicator. Their name and value should be self
    explanatory:

    - TIGHT
    - AVERAGE
    - GOOD
    - UNKNOWN
    """
    TIGHT = "TIGHT"
    AVERAGE = "AVERAGE"
    GOOD = "GOOD"
    UNKNOWN = "UNKNOWN"
