# -*- coding: utf-8 -*-
"""
=======================================================
Parse all the XML available to list all the bundle code
=======================================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from csv import reader
import datetime
from enum import Enum, auto
from io import BytesIO
import json
from logging import info, debug, basicConfig
from os import listdir
from os.path import dirname, join, isdir
from pathlib import Path
from re import sub, compile
import requests
import xml.etree.ElementTree as ElementTree
import sqlalchemy
from zipfile import ZipFile, BadZipFile
import codecs
from pprint import pprint

from enthic.utils.INPI_data_enhancer import decrypt_code_motif
from enthic.utils.conversion import CON_APE, CON_ACC, CON_BUN
from enthic.scraping.database_requests_utils import save_company_to_database, save_metadata_to_database, save_bundle_to_database, get_metadata, save_metadata_ORM, sum_bundle_into_database, replace_bundle_into_database, replace_metadata_ORM, SESSION
from accountability_metadata import AccountabilityMetadata, MetadataCase
from sqlalchemy import select


class ModifiedData(Enum):
    """Enum used to replace or insert data in CSV"""
    ABSENT = auto()
    WRONG_FORMAT = auto()


RE_DENOMINATION = compile(r'\s+|[\t\n]|\xEF')  # NOT AN OBVIOUS PERFORMANCE GAIN...
RE_POSTAL_CODE_TOWN = compile(r"([0-9]+)[ -]?¨?([a-zA-Z0-9`ÀéÉèÈîÎ_ \'\"-\.\(\)\-]+)")
RE_TOWN = compile(r"([a-zA-Z0-9_ \'\"-\.\(\)\-]+)")
RE_POSTAL_CODE = compile(r"([0-9]+)")

################################################################################
# READ CONFIGURATION
with open(join(dirname(__file__), "../", "configuration.json")) as json_configuration_file:
    CONFIG = json.load(json_configuration_file)

################################################################################
# CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
# INPUT
if isdir(CONFIG['inputPath']) is False:
    raise NotADirectoryError(
        "Configuration input path {} does not exist".format(
            CONFIG['inputPath'])
    )

################################################################################
# READ THE CODES TO EXTRACT
ACC_ONT = {}  # EMPTY OBJECT STORING DATA TO EXTRACT
with open(CONFIG['accountOntologyCSV'], mode='r') as infile:
    _reader = reader(infile, delimiter=';')
    next(_reader, None)  # SKIP FIRST LINE, HEADER OF THE CSV
    for rows in _reader:  # ITERATES ALL THE LINES
        try:
            ACC_ONT[rows[3]]["bundleCodeAtt"].append(
                {rows[1]: rows[2].split(",")}
            )
        except KeyError:
            ACC_ONT[rows[3]] = {"bundleCodeAtt": []}

################################################################################
# SET LOG LEVEL
basicConfig(level=CONFIG['debugLevel'],
            format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")

KNOWN_ADDRESS_ERRORS = ["0 | Durée de L'exercice précédentI"]


def read_address_data(address_xml_item, xml_file_name):
    """
    Read the xml's identity's address item, to extract postal_code and town from it

       :param address_xml_item: the identity's address XMl object
       :return: extracted data as a tuple
    """
    postal_code, town = (ModifiedData.ABSENT.value,) * 2
    ####################################################################
    # PARSING THE 'adresse' FIELD, MANY DATA-CAPTURE ERROR.
    try:
        regex_match = RE_POSTAL_CODE_TOWN.match(address_xml_item.text)
        postal_code = regex_match.group(1)
        town = regex_match.group(2).upper()
        if not town.strip():
            postal_code, town = (ModifiedData.WRONG_FORMAT.value,) * 2
    except TypeError as error:
        debug("{0}: {1}".format(str(error),
                                str(address_xml_item.text)))
        postal_code, town = (ModifiedData.WRONG_FORMAT.value,) * 2
    except AttributeError as error:
        try:
            debug("{0}: {1}".format(str(error),
                                    str(address_xml_item.text)))
            regex_match = RE_TOWN.match(address_xml_item.text)
            town = regex_match.group(1).upper()
            postal_code = ModifiedData.WRONG_FORMAT.value
        except AttributeError as error:
            try:
                debug(
                    "{0}: {1}".format(str(error),
                                      str(address_xml_item.text)))
                regex_match = RE_POSTAL_CODE.match(address_xml_item.text)
                town = ModifiedData.WRONG_FORMAT.value
                postal_code = regex_match.group(1)
            except AttributeError as error:
                debug(
                    "{0}: {1}".format(str(error),
                                      str(address_xml_item.text)))
                postal_code, town = \
                    (ModifiedData.WRONG_FORMAT.value,) * 2

    return postal_code, town


def get_siren_data_from_insee_api(siren):
    """
    Get some data from societe.ninja for the given company that sometimes lacks from opendatasoft
        :param siren: the company's siren to search for
    """

    base_url = "https://api.insee.fr/entreprises/sirene/V3/siren/"

    while len(str(siren)) < 9:
        siren = "0" + str(siren)
    url = base_url + str(siren)

    insee_key = CONFIG["INSEE"]["token"]

    response = requests.get(url, headers={"Authorization": insee_key})

    # Check response's status code
    if response.status_code != 200:
        print("Error with url " + url + " got status code " + str(response.status_code))
        print(response.text)
        print(response.request.headers)
    else:
        print("Got INSEE's complementary data from ", url)

    if response.status_code == 401 :
        print("Le token d'accès à l'API INSEE n'est plus valide, veuillez en générer un nouveau pour le mettre dans le fichier de configuration, à partir du site web https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/applications.jag")
        exit()
    content = json.loads(response.text)
    if content["header"]["message"] == "Aucun élément trouvé pour le siren " + str(siren) :
        return None
    if content["header"]["message"] == "Unité légale non diffusable (" + str(siren)+ ")" :
        return None
    code_naf = content["uniteLegale"]["periodesUniteLegale"][0]["activitePrincipaleUniteLegale"]
    denomination = content["uniteLegale"]["periodesUniteLegale"][0]["denominationUniteLegale"]
    if denomination == None:
        denomination = content["uniteLegale"]["prenomUsuelUniteLegale"] + " " + content["uniteLegale"]["periodesUniteLegale"][0]["nomUniteLegale"]
    return denomination, code_naf


def get_siret_data_from_insee_api(siren):
    """
    Get some data from societe.ninja for the given company that sometimes lacks from opendatasoft
        :param siren: the company's siren to search for
    """

    base_url = "https://api.insee.fr/entreprises/sirene/V3/siret?q=siren:"

    url = base_url + str(siren)

    insee_key = CONFIG["INSEE"]["token"]

    response = requests.get(url, headers={"Authorization": insee_key})

    # Check response's status code
    if response.status_code != 200:
        print("Error with url " + url + " got status code " + str(response.status_code))
        print(response.text)
        print(response.request.headers)
    else:
        print("Got INSEE's complementary data from ", url)

    if response.status_code == 401 :
        print("Le token d'accès à l'API INSEE n'est plus valide, veuillez en générer un nouveau pour le mettre dans le fichier de configuration, à partir du site web https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/applications.jag")
        exit()
    content = json.loads(response.text)
    if content["header"]["message"] == "Aucun élément trouvé pour le siren " + str(siren) :
        return None
    if content["header"]["message"] == "Unité légale non diffusable (" + str(siren)+ ")" :
        return None

    postal_code = content["etablissements"][0]["adresseEtablissement"]["codePostalEtablissement"]
    town = content["etablissements"][0]["adresseEtablissement"]["libelleCommuneEtablissement"]
    return postal_code, town

# Dict for conversion of APE code from NAF rév. 1 to NAF rév. 2 (source from https://www.insee.fr/fr/information/2579599)
old_naf_to_new_naf = {
 "07.42C" : "71.12B",
 "07.03D" : "68.32A",
 "07.22A" : "58.29A",
 "01.52Z" : "10.20Z",
 "07.41J" : "70.10Z",
 "08.04D" : "85.59B",
 "05.01Z" : "45.11Z",
 "05.53A" : "56.10A",
 "00.14A" : "01.61Z",
 "05.24W" : "47.64Z",
 "05.02Z" : "45.20A",
 "05.16N" : "46.61Z",
 "01.42A" : "08.12Z",
 "07.48K" : "47.79Z",
 "00.20B" : "02.20Z",
 "09.26C" : "93.29Z",
 "04.53A" : "43.21A",
 "07.23Z" : "62.03Z",
 "07.41G" : "70.22Z",
 "07.22Z" : "62.01Z",
 "05.24L" : "47.54Z",
 "00.12A" : "01.41Z",
 "01.75G" : "13.96Z",
 "05.15L" : "46.75Z",
 "05.15F" : "46.73A",
 "05.13A" : "46.31Z",
 "05.13J" : "46.34Z",
 "06.71C" : "66.30Z",
 "07.14B" : "77.29Z",
 "01.82J" : "14.19Z",
 "07.22C" : "62.02B",
 "05.16K" : "46.69B",
 "09.23H" : "90.01Z",
 "52.4J" : "47.53Z",
 "09.27C" : "93.29Z",
 "01.58C" : "10.71C",
 "05.24Z" : "47.78C",
 "06.02C" : "49.39C",
 "06.52E" : "64.30Z",
 "00.50C" : "03.21Z",
 "04.54M" : "43.39Z",
 "01.58B" : "10.71B",
 "06.33Z" : "79.11Z",
 "07.03C" : "68.32A",
 "04.51A" : "43.12A",
 "05.51B" : "55.10Z",
 "00.11F" : "01.25Z",
 "07.46Z" : "80.10Z",
 "03.32B" : "26.51B",
 "05.24T" : "47.78A",
 "05.18H" : "46.66Z",
 "02.85D" : "25.62B",
 "04.52A" : "41.20A",
 "05.26E" : "47.89Z",
 "01.58D" : "10.71D",
 "02.83C" : "33.20A",
 "03.43Z" : "29.32Z",
 "07.44A" : "73.12Z",
 "03.51E" : "30.12Z",
 "08.04C" : "85.59A",
 "05.512" : "43.12A",
 "05.52E" : "55.20Z",
 "05.14S" : "46.48Z",
 "07.801" : "66.19B",
 "03.12A" : "27.12Z",
 "07.714" : "77.39Z",
 "02.22C" : "18.12Z",
 "06.11A" : "50.10Z",
 "02.81A" : "25.11Z",
 "04.52B" : "41.20B",
 "06.701" : "56.10A",
 "08.51A" : "86.10Z",
 "02.52A" : "22.21Z",
 "05.54C" : "56.30Z",
 "08.111" : "41.10A",
 "08.608" : "90.02Z",
 "05.22P" : "47.29Z",
 "08.002" : "08.12Z",
 "07.42A" : "71.11Z",
 "09.30N" : "96.09Z",
 "05.24R" : "47.62Z",
 "05.560" : "43.99C",
 "04.52U" : "43.99D",
 "02.103" : "25.61Z",

 "65.06" : "45.20A",
 "50.5Z" : "47.30Z",
 "79.06" : "68.31Z",

 "00.12E" : "01.46Z",
 "00.12G" : "01.47Z",
 "00.13Z" : "01.50Z",
 "00.14B" : "81.30Z",
 "00.14D" : "01.62Z",
 "00.20D" : "02.40Z",
 "01.12Z" : "09.10Z",
 "01.53C" : "10.32Z",
 "01.54A" : "10.41A",
 "01.54C" : "10.41B",
 "01.54E" : "10.42Z",
 "01.55A" : "10.51A",
 "01.55B" : "10.51B",
 "01.55C" : "10.51C",
 "01.55D" : "10.51D",
 "01.55F" : "10.52Z",
 "01.56A" : "10.61A",
 "01.56B" : "10.61B",
 "01.57A" : "10.91Z",
 "01.57C" : "10.92Z",
 "01.58F" : "10.72Z",
 "01.58H" : "10.81Z",
 "01.58K" : "10.82Z",
 "01.58P" : "10.83Z",
 "01.58R" : "10.84Z",
 "01.58T" : "10.86Z",
 "01.59A" : "11.01Z",
 "01.59B" : "11.01Z",
 "01.59F" : "11.02A",
 "01.59G" : "11.02B",
 "01.59J" : "11.03Z",
 "01.59L" : "11.04Z",
 "01.59N" : "11.05Z",
 "01.59Q" : "11.06Z",
 "01.59S" : "11.07A",
 "01.59T" : "11.07B",
 "01.60Z" : "12.00Z",
 "01.71A" : "13.10Z",
 "01.71C" : "13.10Z",
 "01.71E" : "13.10Z",
 "01.71F" : "13.10Z",
 "01.71H" : "13.10Z",
 "01.71K" : "13.10Z",
 "01.71M" : "13.10Z",
 "01.71P" : "13.10Z",
 "01.72A" : "13.20Z",
 "01.72C" : "13.20Z",
 "01.72E" : "13.20Z",
 "01.72G" : "13.20Z",
 "01.72J" : "13.20Z",
 "01.73Z" : "13.30Z",
 "01.75A" : "13.93Z",
 "01.75E" : "13.95Z",
 "01.76Z" : "13.91Z",
 "01.77C" : "14.39Z",
 "01.82A" : "14.12Z",
 "01.82C" : "14.13Z",
 "01.82D" : "14.13Z",
 "01.82E" : "14.13Z",
 "01.82G" : "14.14Z",
 "01.91Z" : "15.11Z",
 "01.92Z" : "15.12Z",
 "02.01A" : "16.10A",
 "02.01B" : "16.10B",
 "02.02Z" : "16.21Z",
 "02.11A" : "17.11Z",
 "02.11C" : "17.12Z",
 "02.12A" : "17.21A",
 "02.12B" : "17.21B",
 "02.12C" : "17.21C",
 "02.12G" : "17.23Z",
 "02.12J" : "17.24Z",
 "02.21C" : "58.13Z",
 "02.21E" : "58.14Z",
 "02.21G" : "59.20Z",
 "02.21J" : "58.19Z",
 "02.22A" : "18.11Z",
 "02.22E" : "18.14Z",
 "02.22G" : "18.13Z",
 "02.22J" : "18.13Z",
 "02.23A" : "18.20Z",
 "02.23C" : "18.20Z",
 "02.23E" : "18.20Z",
 "02.31Z" : "19.10Z",
 "02.32Z" : "19.20Z",
 "02.41A" : "20.11Z",
 "02.41C" : "20.12Z",
 "02.41E" : "20.13B",
 "02.41L" : "20.16Z",
 "02.41N" : "20.17Z",
 "02.42Z" : "20.20Z",
 "02.43Z" : "20.30Z",
 "02.44A" : "21.10Z",
 "02.44C" : "21.20Z",
 "02.45C" : "20.42Z",
 "02.46A" : "20.51Z",
 "02.46E" : "20.53Z",
 "02.46G" : "20.59Z",
 "02.46J" : "26.80Z",
 "02.47Z" : "20.60Z",
 "02.51A" : "22.11Z",
 "02.51C" : "22.11Z",
 "02.52C" : "22.22Z",
 "02.61A" : "23.11Z",
 "02.61C" : "23.12Z",
 "02.61E" : "23.13Z",
 "02.61G" : "23.14Z",
 "02.61K" : "23.19Z",
 "02.62A" : "23.41Z",
 "02.62C" : "23.42Z",
 "02.62G" : "23.44Z",
 "02.62J" : "23.49Z",
 "02.62L" : "23.20Z",
 "02.63Z" : "23.31Z",
 "02.64A" : "23.32Z",
 "02.64B" : "23.32Z",
 "02.65A" : "23.51Z",
 "02.65C" : "23.52Z",
 "02.65E" : "23.52Z",
 "02.66A" : "23.61Z",
 "02.66C" : "23.62Z",
 "02.66E" : "23.63Z",
 "02.66G" : "23.64Z",
 "02.66J" : "23.65Z",
 "02.66L" : "23.69Z",
 "02.67Z" : "23.70Z",
 "02.68C" : "23.99Z",
 "02.71Y" : "24.10Z",
 "02.72C" : "24.20Z",
 "02.73A" : "24.31Z",
 "02.73C" : "24.32Z",
 "02.73E" : "24.33Z",
 "02.73G" : "24.34Z",
 "02.74A" : "24.41Z",
 "02.74C" : "24.42Z",
 "02.74D" : "24.42Z",
 "02.74F" : "24.43Z",
 "02.74G" : "24.43Z",
 "02.74J" : "24.44Z",
 "02.74K" : "24.44Z",
 "02.74M" : "24.45Z",
 "02.75A" : "24.51Z",
 "02.75C" : "24.52Z",
 "02.75E" : "24.53Z",
 "02.75G" : "24.54Z",
 "02.84A" : "25.50A",
 "02.84B" : "25.50B",
 "02.84C" : "25.50A",
 "02.85A" : "25.61Z",
 "02.85C" : "25.62A",
 "02.87C" : "25.92Z",
 "02.87E" : "25.93Z",
 "02.87G" : "25.94Z",
 "02.87H" : "25.93Z",
 "02.87J" : "25.93Z",
 "02.95N" : "25.73A",
 "03.14Z" : "27.20Z",
 "03.15A" : "27.40Z",
 "03.15B" : "27.40Z",
 "03.15C" : "27.40Z",
 "03.21D" : "26.12Z",
 "03.33Z" : "33.20C",
 "03.34A" : "32.50B",
 "03.42B" : "29.20Z",
 "03.51A" : "30.11Z",
 "03.51B" : "30.11Z",
 "03.53C" : "30.30Z",
 "03.54A" : "30.91Z",
 "03.54C" : "30.92Z",
 "03.61E" : "31.02Z",
 "03.61G" : "31.09B",
 "03.61H" : "31.09B",
 "03.61J" : "31.09B",
 "03.61M" : "31.03Z",
 "03.62A" : "32.11Z",
 "03.62C" : "32.12Z",
 "03.66A" : "32.13Z",
 "03.66C" : "32.91Z",
 "04.01C" : "35.12Z",
 "04.02A" : "35.21Z",
 "04.03Z" : "35.30Z",
 "04.51B" : "43.12B",
 "04.51D" : "43.13Z",
 "04.52E" : "42.21Z",
 "04.52F" : "42.22Z",
 "04.52J" : "43.91B",
 "04.52K" : "43.99A",
 "04.52L" : "43.91A",
 "04.52N" : "42.12Z",
 "04.52T" : "43.99B",
 "04.52V" : "43.99C",
 "04.53C" : "43.29A",
 "04.53E" : "43.22A",
 "04.53F" : "43.22B",
 "04.54A" : "43.31Z",
 "04.54C" : "43.32A",
 "04.54D" : "43.32B",
 "04.54F" : "43.33Z",
 "04.54H" : "43.34Z",
 "04.54J" : "43.34Z",
 "04.54L" : "43.32C",
 "04.55Z" : "43.99E",
 "05.03A" : "45.31Z",
 "05.03B" : "45.32Z",
 "05.04Z" : "45.40Z",
 "05.05Z" : "47.30Z",
 "05.11A" : "46.11Z",
 "05.11C" : "46.12B",
 "05.11E" : "46.13Z",
 "05.11G" : "46.14Z",
 "05.11J" : "46.15Z",
 "05.11L" : "46.16Z",
 "05.11N" : "46.17B",
 "05.11P" : "46.17A",
 "05.11R" : "46.18Z",
 "05.11T" : "46.19B",
 "05.12A" : "46.21Z",
 "05.12C" : "46.22Z",
 "05.12E" : "46.23Z",
 "05.12G" : "46.24Z",
 "05.12J" : "46.21Z",
 "05.13C" : "46.32A",
 "05.13D" : "46.32B",
 "05.13E" : "46.32C",
 "05.13G" : "46.33Z",
 "05.13L" : "46.35Z",
 "05.13N" : "46.36Z",
 "05.13Q" : "46.37Z",
 "05.13S" : "46.38A",
 "05.13T" : "46.38B",
 "05.13V" : "46.39A",
 "05.13W" : "46.39B",
 "05.14A" : "46.41Z",
 "05.14C" : "46.42Z",
 "05.14D" : "46.42Z",
 "05.14L" : "46.45Z",
 "05.14N" : "46.46Z",
 "05.14Q" : "46.49Z",
 "05.14R" : "46.49Z",
 "05.15A" : "46.71Z",
 "05.15C" : "46.72Z",
 "05.15E" : "46.73A",
 "05.15H" : "46.74A",
 "05.15J" : "46.74B",
 "05.15N" : "46.76Z",
 "05.15Q" : "46.77Z",
 "05.18A" : "46.62Z",
 "05.18C" : "46.63Z",
 "05.18E" : "46.64Z",
 "05.18G" : "46.51Z",
 "05.18J" : "46.52Z",
 "05.18L" : "46.69A",
 "05.18M" : "46.69B",
 "05.18N" : "46.69C",
 "05.18P" : "46.61Z",
 "05.19A" : "46.90Z",
 "05.19B" : "46.90Z",
 "05.21A" : "47.11A",
 "05.21B" : "47.11B",
 "05.21C" : "47.11C",
 "05.21D" : "47.11D",
 "05.21E" : "47.11E",
 "05.21F" : "47.11F",
 "05.21H" : "47.19A",
 "05.21J" : "47.19B",
 "05.22A" : "47.21Z",
 "05.22C" : "47.22Z",
 "05.22E" : "47.23Z",
 "05.22G" : "47.24Z",
 "05.22J" : "47.25Z",
 "05.22L" : "47.26Z",
 "05.22N" : "47.29Z",
 "05.23A" : "47.73Z",
 "05.23C" : "47.74Z",
 "05.23E" : "47.75Z",
 "05.24A" : "47.51Z",
 "05.24C" : "47.71Z",
 "05.24E" : "47.72A",
 "05.24F" : "47.72B",
 "05.24H" : "47.59A",
 "05.24N" : "47.52A",
 "05.24P" : "47.52B",
 "05.24U" : "47.53Z",
 "05.24V" : "47.77Z",
 "05.24X" : "47.76Z",
 "05.24Y" : "47.78B",
 "05.25Z" : "47.79Z",
 "05.26A" : "47.91A",
 "05.26B" : "47.91B",
 "05.26D" : "47.81Z",
 "05.26G" : "47.99A",
 "05.26H" : "47.99B",
 "05.27A" : "95.23Z",
 "05.27C" : "95.21Z",
 "05.27D" : "95.22Z",
 "05.27F" : "95.25Z",
 "05.51A" : "55.10Z",
 "05.51C" : "55.10Z",
 "05.51E" : "55.10Z",
 "05.52C" : "55.30Z",
 "05.52F" : "55.90Z",
 "05.53B" : "56.10C",
 "05.54A" : "56.30Z",
 "05.54B" : "56.30Z",
 "05.55A" : "56.29B",
 "05.55C" : "56.29A",
 "05.55D" : "56.21Z",
 "06.02A" : "49.31Z",
 "06.02B" : "49.39A",
 "06.02E" : "49.32Z",
 "06.02G" : "49.39B",
 "06.02L" : "49.41B",
 "06.02M" : "49.41A",
 "06.02N" : "49.42Z",
 "06.02P" : "49.41C",
 "06.03Z" : "49.50Z",
 "06.31A" : "52.24A",
 "06.31B" : "52.24B",
 "06.31D" : "52.10A",
 "06.31E" : "52.10B",
 "06.34A" : "52.29A",
 "06.34B" : "52.29B",
 "06.41C" : "53.20Z",
 "06.51A" : "64.11Z",
 "06.51C" : "64.19Z",
 "06.51D" : "64.19Z",
 "06.51E" : "64.19Z",
 "06.51F" : "64.19Z",
 "06.52A" : "64.91Z",
 "06.52F" : "64.99Z",
 "06.60E" : "65.12Z",
 "06.60F" : "65.20Z",
 "06.60G" : "65.12Z",
 "06.71A" : "66.11Z",
 "07.01A" : "41.10A",
 "07.01B" : "41.10B",
 "07.01D" : "41.10D",
 "07.01F" : "68.10Z",
 "07.02A" : "68.20A",
 "07.02B" : "68.20B",
 "07.02C" : "68.20B",
 "07.03A" : "68.31Z",
 "07.11A" : "77.11A",
 "07.11B" : "77.11B",
 "07.12C" : "77.34Z",
 "07.12E" : "77.35Z",
 "07.13A" : "77.31Z",
 "07.13C" : "77.32Z",
 "07.13E" : "77.33Z",
 "07.13G" : "77.39Z",
 "07.21Z" : "62.02A",
 "07.26Z" : "62.09Z",
 "07.32Z" : "72.20Z",
 "07.41A" : "69.10Z",
 "07.41C" : "69.20Z",
 "07.41E" : "73.20Z",
 "07.43A" : "71.20A",
 "07.43B" : "71.20B",
 "07.45B" : "78.20Z",
 "07.48A" : "74.20Z",
 "07.48B" : "74.20Z",
 "07.48D" : "82.92Z",
 "07.48G" : "82.19Z",
 "07.48H" : "82.20Z",
 "07.48J" : "82.30Z",
 "07.51A" : "84.11Z",
 "07.51C" : "84.12Z",
 "07.51E" : "84.13Z",
 "07.52C" : "84.22Z",
 "07.52E" : "84.23Z",
 "07.52G" : "84.24Z",
 "07.52J" : "84.25Z",
 "07.53A" : "84.30A",
 "07.53B" : "84.30B",
 "07.53C" : "84.30C",
 "08.02A" : "85.31Z",
 "08.02C" : "85.32Z",
 "08.51E" : "86.23Z",
 "08.51J" : "86.90A",
 "08.51K" : "86.90B",
 "08.51L" : "86.90C",
 "08.52Z" : "75.00Z",
 "08.53G" : "88.91A",
 "09.00A" : "37.00Z",
 "09.11A" : "94.11Z",
 "09.11C" : "94.12Z",
 "09.12Z" : "94.20Z",
 "09.13A" : "94.91Z",
 "09.13C" : "94.92Z",
 "09.13E" : "94.99Z",
 "09.21A" : "59.11A",
 "09.21B" : "59.11B",
 "09.21C" : "59.11C",
 "09.21F" : "59.13A",
 "09.21G" : "59.13B",
 "09.21J" : "59.14Z",
 "09.22B" : "59.11A",
 "09.22D" : "60.20A",
 "09.22E" : "60.20B",
 "09.23B" : "90.02Z",
 "09.23F" : "93.21Z",
 "09.25A" : "91.01Z",
 "09.25E" : "91.04Z",
 "09.26A" : "93.11Z",
 "09.27A" : "92.00Z",
 "09.30A" : "96.01A",
 "09.30B" : "96.01B",
 "09.30D" : "96.02A",
 "09.30E" : "96.02B",
 "09.30G" : "96.03Z",
 "09.30H" : "96.03Z",
 "09.30K" : "96.04Z",
 "09.50Z" : "97.00Z",
 "09.60Z" : "98.10Z",
 "09.70Z" : "98.20Z",
 "09.90Z" : "99.00Z"
  }


def read_identity_data(identity_xml_item, xml_file_name):
    """
    Read the xml's identity item, to extract useful data from it

       :param identity_xml_item: the identity XMl object
       :return: extracted data as a tuple
    """
    acc_type, siren, denomination, year, ape, \
    postal_code, town, code_motif, info_traitement, \
    code_confidentialite, duree_exercice, date_cloture_exercice = (None,) * 12

    unknown_ape_codes = ["00.00Z", "00.0Z", "00.000", "00.097"]
    for identity in identity_xml_item:  # identite LEVEL
        if identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}siren':
            siren = int(identity.text)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_type_bilan':
            acc_type = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}denomination':
            # If denomination contain weird character, get denomination from INSEE's API
            if "�" in identity.text or "�" in identity.text or "�" in identity.text or "" in identity.text or "�" in identity.text or "µ" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text or "" in identity.text:
                identity.text, dummy = get_siren_data_from_insee_api(siren)
            # REMOVE MULTIPLE WHITESPACES, TABULATION, NEW LINE, THEN SWITCH TO UPPER CASE
            denomination = sub(RE_DENOMINATION, " ", identity.text).strip(" ").upper()
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_motif':
            code_motif = decrypt_code_motif(identity.text)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_confidentialite':
            code_confidentialite = int(identity.text)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}info_traitement':
            info_traitement = identity.text.replace(' ', '') if identity.text else None
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}date_cloture_exercice':
            date_cloture_exercice = datetime.datetime.strptime(identity.text, "%Y%m%d").date()
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}adresse':
            postal_code, town = read_address_data(identity, xml_file_name)
            if len(str(postal_code)) > 5 :
                postal_code, town = get_siret_data_from_insee_api(siren)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}duree_exercice_n':
            duree_exercice = int(identity.text)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_activite':
            ape_with_dot = identity.text[:2] + "." + identity.text[2:]
            if ape_with_dot in CON_APE: # Find enthic integer from given ape code
                ape = str(CON_APE[ape_with_dot])
            elif ape_with_dot in old_naf_to_new_naf: # Try to convert given apecode from old naf to new naf
                ape = str(CON_APE[old_naf_to_new_naf[ape_with_dot]])
            else : # Try to fetch ape code from INSEE's API
                ape_from_insee = None
                try :
                    dummy, ape_from_insee = get_siren_data_from_insee_api(siren)
                except TypeError as e:
                    print("Le numéro siren", siren, "n'est pas dispo via l'API de l'INSEE")
                if ape_from_insee in CON_APE:
                    ape = str(CON_APE[ape_from_insee])
                elif ape_from_insee in old_naf_to_new_naf:
                    ape = str(CON_APE[old_naf_to_new_naf[ape_from_insee]])
                elif ape_from_insee in unknown_ape_codes or ape_with_dot in unknown_ape_codes:
                        ape = str(CON_APE["00.00"])
                else :
                    print("N'a pas pu trouvé le code APE correspondant à celui du XML (", ape_with_dot, ") ou de l'INSEE (", ape_from_insee, ")")
                    exit()

    if duree_exercice <= date_cloture_exercice.month or duree_exercice - date_cloture_exercice.month <= date_cloture_exercice.month:
        year = date_cloture_exercice.year
    else :
        year = date_cloture_exercice.year - 1

    return acc_type, siren, denomination, year, ape, postal_code, town, \
           code_motif, code_confidentialite, info_traitement, duree_exercice, date_cloture_exercice


def process_xml_file(xml_stream, xml_name):
    """
    Process an xml file already opened
    """
    ####################################################
    # XML PARSER
    try :
        tree = ElementTree.parse(xml_stream)
    except ElementTree.ParseError as error :
        info("Error processing XML " + xml_name + " : {}".format(error))
        return False
    root = tree.getroot()
    ####################################################
    # XML RELATED VARIABLES
    acc_type, siren, year = (None,) * 3
    ####################################################
    # ITERATE ALL TAGS
    metadata_case = MetadataCase.IS_NEW
    bundles_added_set = set()
    for child in root[0]:
        ################################################
        # IDENTITY TAGS, SIREN AND TYPE OF ACCOUNTABILITY
        if child.tag == "{fr:inpi:odrncs:bilansSaisisXML}identite":
            acc_type, siren, denomination, year, ape, \
            postal_code, town, code_motif, \
            code_confidentialite, info_traitement, duree_exercice, date_cloture_exercice = read_identity_data(child, xml_name)
            ############################################
            # WRITE IDENTITY FILE IF ACCOUNT TYPE IS
            # KNOWN
            if not acc_type in ACC_ONT.keys():
                return False
            existing_metadata_list = get_metadata(siren)
            new_metadata = AccountabilityMetadata(siren=siren, declaration=year, duree_exercice=duree_exercice, date_cloture_exercice=date_cloture_exercice, code_motif=code_motif, code_confidentialite=code_confidentialite, info_traitement=info_traitement, accountability=acc_type)

            metadata_to_replace = None
            for existing_metadata in existing_metadata_list:
                result = new_metadata.compare(existing_metadata)
                if result == MetadataCase.IGNORE:
                    return False
                if result == MetadataCase.REPLACE:
                    metadata_to_replace = existing_metadata
                    metadata_case = result
                if result != MetadataCase.IS_NEW and metadata_case != MetadataCase.REPLACE:
                    metadata_case = result

            if len(existing_metadata_list) == 0:
                save_company_to_database(str(siren), str(denomination), str(ape), str(postal_code), str(town))
            else :
                print("New metadata", new_metadata, "different des metadata déjà en base. Action choisie :", metadata_case)
                pprint(existing_metadata_list)

            if metadata_case == MetadataCase.REPLACE :
                replace_metadata_ORM(new_metadata, metadata_to_replace)
            else:
                save_metadata_ORM(new_metadata)
        ################################################
        # BUNDLE TAGS IN PAGES TO ITERATE WITH BUNDLE CODES
        # AND AMOUNT
        elif child.tag == "{fr:inpi:odrncs:bilansSaisisXML}detail":
            for page in child:
                for bundle in page:
                    try:
                        for bundle_code in \
                                ACC_ONT[acc_type]['bundleCodeAtt']:
                            if bundle.attrib["code"] in bundle_code.keys():
                                for amount_code in bundle_code[bundle.attrib["code"]]:
                                    amount_code = "m{0}".format(amount_code)
                                    if metadata_case == MetadataCase.COMPLEMENTARY:
                                        sum_bundle_into_database(siren, str(year),
                                                                str(CON_ACC[acc_type]),
                                                                str(CON_BUN[CON_ACC[
                                                                    acc_type]][
                                                                        bundle.attrib[
                                                                            "code"]]),
                                                                str(int(
                                                                    bundle.attrib[
                                                                        amount_code]
                                                                )))
                                    elif metadata_case == MetadataCase.REPLACE:
                                        replace_bundle_into_database(siren, str(year),
                                                                str(CON_ACC[acc_type]),
                                                                str(CON_BUN[CON_ACC[
                                                                    acc_type]][
                                                                        bundle.attrib[
                                                                            "code"]]),
                                                                str(int(
                                                                    bundle.attrib[
                                                                        amount_code]
                                                                )), False)
                                    elif metadata_case == MetadataCase.IS_NEW:
                                        new_bundle = (siren, str(year),
                                                                str(CON_ACC[acc_type]),
                                                                str(CON_BUN[CON_ACC[
                                                                    acc_type]][
                                                                        bundle.attrib[
                                                                            "code"]]),
                                                                str(int(
                                                                    bundle.attrib[
                                                                        amount_code]
                                                                )))
                                        if new_bundle[:4] in bundles_added_set:
                                            print("Bundle", new_bundle, "en double dans le fichier XML")
                                        else:
                                            bundles_added_set.add(new_bundle[:4])
                                            save_bundle_to_database(new_bundle[0], new_bundle[1], new_bundle[2], new_bundle[3], new_bundle[4])
                    except KeyError as key_error:
                        debug("{} in account {} bundle {}".format(
                            key_error,
                            acc_type,
                            bundle.attrib[
                                "code"]
                        ))
    SESSION.commit()
    return True


def process_daily_zip_file(daily_zip_file_path):
    try:  # SOME BAD ZIP FILES ARE IN THE DATASET
        input_zip = ZipFile(daily_zip_file_path)
        for zipped_xml_name in input_zip.namelist():  # LIST ARCHIVES IN ZIP
            try:
                zipped_xml = ZipFile(BytesIO(input_zip.read(zipped_xml_name)))
                # SUPPOSED ONLY ONE XML BUT ITERATE TO BE SURE
                for xml in zipped_xml.namelist():
                    process_xml_file(BytesIO(zipped_xml.open(xml).read()), zipped_xml_name)
            except UnicodeDecodeError as error:
                debug(error)
    except BadZipFile as error:  #  TODO REPORT ERROR TO INPI
        info(error)
        exit()


def main():
    """
    Based on the configuration storing the input file path. All the xml are
    read to list the bundle code.
    """
    ############################################################################
    # CREATING A LIST OF THE BUNDLE XML CODES, ZIP ARE READ IN BtesIO, IN ORDER
    # TO BREAK FILE SYSTEM. TOO MUCH ZIP DISTURB THE FS.
    for file in listdir(CONFIG['inputPath']):  # LIST INPUT FILES
        info("processing INPI daily zip file %s", file)
        if file.endswith(".zip"):  # ONLY PROCESS ZIP FILES
            process_daily_zip_file(join(CONFIG['inputPath'], file))


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
