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
import re

from enthic.ontology import APE_CODE, ONTOLOGY

################################################################################
# CREATE DICTIONARY WHERE keys ARE 'official APE code' AND values ARE 'enthic APE code'
CON_APE = {}
for key, value in APE_CODE.items():
    CON_APE[value[0]] = key

# CREATE DICTIONARY FROM ONTOLOGY TO CONVERT str TO int
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


def get_corresponding_ape_codes(ape_code):
    """
    APE codes are not saved in the original format.
    This function returns codes that are in the database
    and corresponds to the given APE code or it's sub-categories
    It returns None if the given APE code does not exist

        :param ape_code : the list of APE for the filter, comma separated

        :return: list of corresponding APE_CODE in database
    """
    result = list()
    for one_code in ape_code.split(","):
        for i in APE_CODE:
            if re.match(one_code, APE_CODE[i][0]):
                result.append(i)
    if not result:
        return None
    return result
