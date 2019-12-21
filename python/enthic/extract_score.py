# -*- coding: utf-8 -*-
"""
=================================================
Extract DIR (distribution radio) and FJ (revenue)
=================================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from csv import reader
from json import load
from logging import basicConfig
from os.path import isdir, join, dirname


def main():
    """
    Based on the configuration storing the input file path. Extract DIR
    (distribution radio) and FJ (revenue) of a given company for a given year.
    """
    ############################################################################
    # CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
    # INPUT
    with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
        config = load(json_configuration_file)
    # OUTPUT
    if isdir(config['outputPath']) is False:
        raise NotADirectoryError(
            "Configuration output path {} does not exist".format(
                config['inputPath'])
        )
    ############################################################################
    # SET LOG LEVEL
    basicConfig(level=config['debugLevel'], format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")

    ############################################################################
    # READ THE INPUT FILE AND PRINT THE OUTPUT
    with open(join(config['outputPath'], config['scoreBundleFile']), mode='r') as infile:
        _reader = reader(infile, delimiter=';')  # READER OF THE INPUT CSV FILE
        key, distribution_ratio, revenue = (None,) * 3
        for rows in _reader:  # ITERATE EACH LINE
            if rows[2] == "DIR":
                distribution_ratio = int(rows[3])
            elif rows[2] == "FJ":
                revenue = int(rows[3])
            if key != rows[0]:  # KEY BREAK ON COMPANY
                if revenue is not None and distribution_ratio is not None:
                    print(str(distribution_ratio) + ";" + str(revenue))
                    key, distribution_ratio, revenue = (None,) * 3
            else:
                key = rows[0]


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
