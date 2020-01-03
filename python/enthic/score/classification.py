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


class DistributionClassification(Enum):
    TIGHT = "TIGHT"
    AVERAGE = "AVERAGE"
    GOOD = "GOOD"
    UNKNOWN = "UNKNOWN"
