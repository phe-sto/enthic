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
from os.path import join, isdir
from enthic.utils import CONFIG
from logging import debug
from csv import writer, reader

# OUTPUT
if isdir(CONFIG['outputPath']) is False:
    raise NotADirectoryError(
        "Configuration output path {} does not exist".format(
            CONFIG['outputPath'])
    )


def main():
    """
    Based on the configuration storing the input file path. Sum all the bundle
    of the year for one company.
    """
    ############################################################################
    # RESULT FILE
    bundle_file = open(join(CONFIG['outputPath'], CONFIG['bundleCSV']), "w")
    bundle_writer = writer(bundle_file, delimiter=CONFIG['csvSeparator'])
    ############################################################################
    # READ THE INPUT FILE AND bundle_file.write THE OUTPUT
    with open(join(CONFIG['outputPath'], CONFIG['sortBundleTmpFile']), mode='r') as infile:
        _reader = reader(infile, delimiter=CONFIG['csvSeparator'])  # READER OF THE INPUT CSV FILE
        key = None
        for row in _reader:  # ITERATE EACH LINE
            if key is not None and key < row[0:4]:  # KEY BREAK ON BUNDLE CODE
                bundle_writer.writerow((key[0], key[1], key[2], key[3], bundle))
            key = row[0:4]
            bundle = row[4]
        else:
            debug("Find two identical keys %s" % str(key))
        # WRITE THE LAST LINE
        bundle_writer.writerow((key[0], key[1], key[2], key[3], bundle))
    bundle_file.close()


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
