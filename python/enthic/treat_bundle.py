# -*- coding: utf-8 -*-
"""
=====================================================================
Sum all the bundle of the year for one company from a CSV sorted file
=====================================================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or bundle_file.write, just log and files.
"""
from csv import reader
from json import load
from logging import basicConfig
from os.path import isdir, join, dirname


def main():
    """
    Based on the configuration storing the input file path. Sum all the bundle
    of the year for one company.
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
    basicConfig(level=config['debugLevel'],
                format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    ############################################################################
    # RESULT FILE
    bundle_file = open(join(config['outputPath'], config['scoreBundleFile']), "w")
    ############################################################################
    # READ THE INPUT FILE AND bundle_file.write THE OUTPUT
    with open(join(config['outputPath'], config['sortBundleFile']), mode='r') as infile:
        _reader = reader(infile, delimiter=';')  # READER OF THE INPUT CSV FILE
        key, bundle_sum, gain, distribution = (None,) * 4
        for rows in _reader:  # ITERATE EACH LINE
            if key is not None and key < rows[0:3]:  # KEY BREAK ON BUNDLE CODE
                bundle_file.write(
                    key[0] + ";" + key[1] + ";" + key[2] + ";" + str(bundle_sum) + ";\n")
            if key is not None and key < rows[0:2]:  # KEY BREAK ON COMPANY PER YEAR
                if distribution is not None:
                    bundle_file.write(
                        key[0] + ";" + key[1] + ";" + "DIS" + ";" + str(distribution) + ";\n")
                if gain is not None:
                    bundle_file.write(key[0] + ";" + key[1] + ";" + "GAN" + ";" + str(gain) + ";\n")
                if gain is not None and distribution is not None:
                    if gain != 0:
                        bundle_file.write(
                            key[0] + ";" + key[1] + ";" + "DIR" + ";" + str(
                                round(distribution / gain, 2)) + ";\n")
            if key == rows[0:3]:  # SAME KEY, SUM THE BUNDLE AMOUNT
                bundle_sum += int(rows[3])
                if rows[2] in config["gainCodes"]:
                    gain += int(rows[3])
                if rows[2] in config["distributionCodes"]:
                    distribution += int(rows[3])
            else:
                key = rows[0:3]  # NEW KEY INITIATE BUNDLE AMOUNT
                bundle_sum = int(rows[3])
                if rows[2] in config["gainCodes"]:
                    gain = int(rows[3])
                if rows[2] in config["distributionCodes"]:
                    distribution = int(rows[3])
    bundle_file.close()


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
