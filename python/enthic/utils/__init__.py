# -*- coding: utf-8 -*-
from json import load
from logging import basicConfig
from os.path import join, dirname
from pathlib import Path

################################################################################
# CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
# INPUT
with open(join(Path(dirname(__file__)).parent.absolute(), "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)
################################################################################
# SET LOG LEVEL
basicConfig(level=CONFIG['debugLevel'],
            format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
