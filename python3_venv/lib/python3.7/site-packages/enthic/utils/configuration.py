# -*- coding: utf-8 -*-
"""
================================================================================
social.utils.CONFIG initialize the CONFIG object based on the configuration JSON
================================================================================
"""

from argparse import ArgumentParser
from json import load

parser = ArgumentParser()
parser.add_argument("-c", type=str, default="configuration.json",
                    help="file path to the configuration.json")
args = parser.parse_args()
with open(args.c) as json_configuration_file:
    config = load(json_configuration_file)
