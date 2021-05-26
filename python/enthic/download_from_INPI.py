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
from glob import glob
import subprocess
from argparse import ArgumentParser
from io import BytesIO
import sys
from json import load
from ftplib import FTP_TLS
import shutil
import urllib
import wget
from py7zr import SevenZipFile
from logging import info, error

from enthic.extract_bundle import process_daily_zip_file, process_xml_file


################################################################################
# READ CONFIGURATION
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)

FTP_MAX_VOLUME = 6 * 1024 * 1024 * 1024  # Default is 6 GigaBytes
FTP_VOLUME_USED = 0  # Bytes
IMPORT_HISTORIC = []

def add_data_to_database(file_path, date_processed):
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

    shutil.rmtree(CONFIG['inputPath'] + "/comptes")
    files = glob(CONFIG['inputPath'] + "/PUB_CA*")
    for f in files:
        os.remove(f)

    if result.stdout:
        raise Exception("Following error while loading data from file "
                        + file_path + " into database : \n"
                        + result.stdout.decode('utf-8'))
    else:
        os.remove(join(CONFIG['outputPath'], CONFIG['tmpBundleFile']))
        os.remove(join(CONFIG['outputPath'], CONFIG['identityFile']))
        os.remove(join(CONFIG['outputPath'], CONFIG['metadataFile']))
        os.remove(file_path)
        IMPORT_HISTORIC.append(date_processed)
        with open(CONFIG["importHistoricFile"], 'a') as import_historic_file:
            import_historic_file.write(date_processed + "\n")


def explore_and_process_FTP_folder(folderToExplore):
    """
    Recursive function that explore FTP to download every daily zip files

    :param folderToExplore: folder to explore
    """
    info("Exploring INPI's FTP folder " + folderToExplore)
    ftp = FTP_TLS('opendata-rncs.inpi.fr')
    ftp.login(user=CONFIG["INPI"]["user"], passwd=CONFIG["INPI"]["password"])
    ftp.prot_p()
    connexion = True
    element_list = ftp.nlst(folderToExplore)
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
            explore_and_process_FTP_folder(element)

    if connexion:
        ftp.quit()


def explore_and_process_CQuest_mirror():
    """
    Function that explore CQuest mirror to download every daily zip files

    """
    for year in range(2017, 2021):
        url = 'http://data.cquest.org/inpi_rncs/comptes/' + str(year) + '/'
        for month in range(1, 12):
            for day in range(1, 31):
                date = str(year) + str(month).zfill(2) + str(day).zfill(2)
                if date in IMPORT_HISTORIC :
                    continue
                file_name = 'bilans_saisis_' + date + ".7z"
                print("downloading : ", url + file_name)
                localfile_path = join(CONFIG['inputPath'], basename(file_name))
                try:
                    wget.download(url + file_name, localfile_path)
                    with SevenZipFile(localfile_path, mode='r') as z:
                        z.extractall(path=CONFIG['inputPath'])
                    for filename in os.listdir(join(CONFIG['inputPath'], "comptes/")):
                        xml_path = join(CONFIG['inputPath'],
                                        "comptes/",
                                        filename)
                        xml_file_opened = open(xml_path, "rb")
                        bytes_io = BytesIO(xml_file_opened.read())
                        process_xml_file(bytes_io, filename)
                    add_data_to_database(localfile_path, date)
                except urllib.error.HTTPError as error:
                    print(url + file_name + " doesn't exist : ", error)


def main():
    """
    Download INPI's daily file into input folder, as stated in configuration file.
    """
    global FTP_MAX_VOLUME
    global IMPORT_HISTORIC

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

    try :
        with open(CONFIG["importHistoricFile"], 'r') as import_historic_file:
            for line in import_historic_file:
                IMPORT_HISTORIC.append(line.strip())
    except FileNotFoundError:
        open(CONFIG["importHistoricFile"], 'x') # Create file

    explore_and_process_CQuest_mirror()
    # explore_and_process_FTP_folder(args.folder)


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
