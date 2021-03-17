# -*- coding: utf-8 -*-
"""
===================
Set of function to help handle errors in data from INPI
===================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from enthic.ontology import CODE_MOTIF


def decrypt_code_motif(raw_code):
    """
    try to convert code_motif as in the XML file, to known value described in CODE_MOTIF

        :param raw_code: code as written in XML files
        :return: valid code
    """
    try:
        simplified_code = str(int(raw_code)) # To suppress leading zero
        if simplified_code in CODE_MOTIF:
            return simplified_code
    except ValueError:
        if raw_code in CODE_MOTIF:
            return raw_code
    # raw code isn't valid, so don't change it
    return raw_code
