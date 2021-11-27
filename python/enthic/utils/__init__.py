# -*- coding: utf-8 -*-
from json import load
from logging import basicConfig
from os.path import join, dirname

################################################################################
# CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
# INPUT
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)
################################################################################
# SET LOG LEVEL
basicConfig(level=CONFIG['debugLevel'],
            format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
