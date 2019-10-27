# -*- coding: utf-8 -*-
"""
==============================================
Sum all the bundle of the year for one company
==============================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from csv import reader
from logging import basicConfig
from os.path import isdir, join

from enthic.utils.configuration import config


def main():
    """
    Based on the configuration storing the input file path. Sum all the bundle
       of the year for one company
    """
    ############################################################################
    # CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
    # INPUT
    if isdir(config['inputPath']) is False:
        raise NotADirectoryError(
            "Configuration input path {} does not exist".format(
                config['inputPath'])
        )
    # OUTPUT
    if isdir(config['outputPath']) is False:
        raise NotADirectoryError(
            "Configuration output path {} does not exist".format(
                config['inputPath'])
        )
    ############################################################################
    # SET LOG LEVEL
    basicConfig(level=config['debugLevel'])
    ############################################################################
    # READ THE INPUT FILE AND PRINT THE OUPUT
    with open(join(config['outputPath'], config['sortBundleFile']), mode='r') as infile:
        _reader = reader(infile, delimiter=';')  # READER OF THE INPUT CSV FILE
        key, bundle_sum = (None,) * 2
        for rows in _reader:  # ITERATE EACH LINE
            if key is not None and key < rows[0:3]:  # KEY BREAK
                print(key[0] + ";" + key[1] + ";" + key[2] + ";" + str(bundle_file) + ";")
            if key == rows[0:3]:  # SAME KEY, SUM THE BUNDLE AMOUNT
                bundle_file += int(rows[3])
            else:
                key = rows[0:3]  # NEW KEY INITIATE BUNDLE AMOUNT
                bundle_file = int(rows[3])


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
