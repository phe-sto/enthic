# -*- coding: utf-8 -*-
"""
========================================
Download daily zip files from INPI's FTP
========================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from os.path import dirname, join, basename, abspath, pardir
import os
import subprocess
from argparse import ArgumentParser
import sys
from json import load
from ftplib import FTP_TLS
from logging import info

from enthic.extract_bundle import process_daily_zip_file


################################################################################
# READ CONFIGURATION
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)

FTP_MAX_VOLUME = 6 * 1024 * 1024 * 1024  # Default is 6 GigaBytes
FTP_VOLUME_USED = 0  # Bytes


def add_data_to_database(file_path):
    """
        Add data contained in the given file into MySQL database
        then delete temporary files if it's a success

        :param file_path: daily INPI file to add to database
    """
    # Load new data into database
    filling_script = abspath(join(".", pardir, "sh", "database-filling.sh"))
    result = subprocess.run([filling_script, CONFIG["mySQL"]["enthic"]["password"]],
                            stdout=subprocess.PIPE,
                            check=True)

    if result.stdout:
        raise Exception("Following error while loading data from file "
                        + file_path + " into database : \n"
                        + result.stdout.decode('utf-8'))

    os.remove(join(CONFIG['outputPath'], CONFIG['tmpBundleFile']))
    os.remove(join(CONFIG['outputPath'], CONFIG['identityFile']))
    os.remove(join(CONFIG['outputPath'], CONFIG['metadataFile']))
    os.remove(file_path)


def explore_and_process_ftp_folder(folder_to_explore):
    """
    Recursive function that explore FTP to download every daily zip files

    :param folder_to_explore: folder to explore
    """
    info("Exploring INPI's FTP folder " + folder_to_explore)
    ftp = FTP_TLS('opendata-rncs.inpi.fr')
    ftp.login(user=CONFIG["INPI"]["user"], passwd=CONFIG["INPI"]["password"])
    ftp.prot_p()
    connexion = True
    element_list = ftp.nlst(folder_to_explore)
    for element in element_list:
        if element.endswith(".zip"):
            if FTP_VOLUME_USED + ftp.size(element) > FTP_MAX_VOLUME:
                info("FTP download volume limit reached, stopping everything")
                sys.exit(3)
            localfile_path = join(CONFIG['inputPath'], basename(element))
            localfile = open(localfile_path, 'wb')
            info("Downloading file " + element + " into file " + localfile_path)
            ftp.retrbinary("RETR " + element, localfile.write)
            # extract data from xml files to csv files
            process_daily_zip_file(localfile_path)
            # add csv to database
            add_data_to_database(localfile_path)
        elif element.endswith(".md5"):
            continue
        else:
            if connexion:
                ftp.quit()
                connexion = False
            explore_and_process_ftp_folder(element)

    if connexion:
        ftp.quit()


def main():
    """
    Download INPI's daily file into input folder, as stated in configuration file.
    """
    global FTP_MAX_VOLUME

    parser = ArgumentParser(description='Download data and add it to Enthic database')
    parser.add_argument('quota',
                        metavar='Quota',
                        type=int,
                        help='Maximum number of Gio that can be download from server')

    parser.add_argument('folder',
                        metavar="Folder",
                        type=ascii,
                        help='FTP folder where download should start')

    args = parser.parse_args()
    FTP_MAX_VOLUME = args.quota * 1024 * 1024 * 1024

    explore_and_process_ftp_folder(args.folder)


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
