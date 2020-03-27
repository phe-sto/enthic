# -*- coding: utf-8 -*-
"""
===============================================================================
Set of function converting the ontology from INPI format to base integer format
===============================================================================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enthic.ontology import APE_CODE, ONTOLOGY

################################################################################
# CREATE DICTIONARY FROM ONTOLOGY TO CONVERT str TO int
CON_APE = {}
for key, value in APE_CODE.items():
    CON_APE[value[0]] = key

CON_ACC = {}
for key, value in ONTOLOGY["accounting"].items():
    CON_ACC[value[0]] = key

CON_BUN = {}
for key, value in ONTOLOGY["accounting"].items():
    CON_BUN[key] = {}
    for int_bundle, dict_bun in value["code"].items():
        try:
            CON_BUN[key][dict_bun[0]] = int_bundle
        except KeyError:
            continue
