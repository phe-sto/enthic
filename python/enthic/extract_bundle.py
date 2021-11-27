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
import xml.etree.ElementTree as ElementTree
from csv import reader, writer
from enum import Enum, auto
from io import BytesIO
from json import load
from logging import info, debug, basicConfig
from os import listdir
from os.path import dirname, join, isdir
from re import sub, compile
from zipfile import ZipFile, BadZipFile

from enthic.utils.INPI_data_enhancer import decrypt_code_motif
from enthic.utils.conversion import CON_APE, CON_ACC, CON_BUN


class ModifiedData(Enum):
    """Enum used to replace or insert data in CSV"""
    ABSENT = auto()
    WRONG_FORMAT = auto()


RE_DENOMINATION = compile(r'\s+|[\t\n]')  # NOT AN OBVIOUS PERFORMANCE GAIN...
RE_POSTAL_CODE_TOWN = compile(r"([0-9]+)[ -]?¨?([a-zA-Z0-9`ÀéÉèÈîÎ_ \'\"-\.\(\)\-]+)")
RE_TOWN = compile(r"([a-zA-Z0-9_ \'\"-\.\(\)\-]+)")
RE_POSTAL_CODE = compile(r"([0-9]+)")

################################################################################
# READ CONFIGURATION
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    CONFIG = load(json_configuration_file)

################################################################################
# CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
# INPUT
if isdir(CONFIG['inputPath']) is False:
    raise NotADirectoryError(
        "Configuration input path {} does not exist".format(
            CONFIG['inputPath'])
    )
# OUTPUT
if isdir(CONFIG['outputPath']) is False:
    raise NotADirectoryError(
        "Configuration output path {} does not exist".format(
            CONFIG['outputPath'])
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


def read_identity_data(identity_xml_item, xml_file_name):
    """
    Read the xml's identity item, to extract useful data from it

       :param identity_xml_item: the identity XMl object
       :return: extracted data as a tuple
    """
    acc_type, siren, denomination, year, ape, \
    postal_code, town, code_motif, info_traitement, \
    code_confidentialite = (ModifiedData.ABSENT.value,) * 10

    for identity in identity_xml_item:  # identite LEVEL
        if identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}siren':
            siren = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_type_bilan':
            acc_type = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}denomination':
            # REMOVE MULTIPLE WHITESPACES, TABULATION, NEW LINE, THEN SWITCH TO UPPER CASE
            denomination = sub(RE_DENOMINATION, " ", identity.text).strip(" ").upper()
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_motif':
            code_motif = decrypt_code_motif(identity.text)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_confidentialite':
            code_confidentialite = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}info_traitement':
            info_traitement = identity.text.replace(' ', '') if identity.text else ModifiedData.ABSENT.value
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}date_cloture_exercice':
            year = identity.text[:4]
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}adresse':
            postal_code, town = read_address_data(identity, xml_file_name)
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_activite':
            try:
                ape = str(CON_APE[identity.text])
            except KeyError:
                ape = 1672

    return acc_type, siren, denomination, year, ape, postal_code, town, \
           code_motif, code_confidentialite, info_traitement


def process_daily_zip_file(daily_zip_file_path):
    ############################################################################
    # OPEN OUTPUT FILES TO APPEND NEW DATA
    bundle_file = open(join(CONFIG['outputPath'], CONFIG['tmpBundleFile']), "a")
    identity_file = open(join(CONFIG['outputPath'], CONFIG['identityFile']), "a")
    csv_separator = CONFIG['csvSeparator']
    ############################################################################
    # Declare writers
    bundle_writer = writer(bundle_file, delimiter=csv_separator)
    identity_writer = writer(identity_file, delimiter=csv_separator)
    try:  # SOME BAD ZIP FILE ARE IN HE DATASET
        input_zip = ZipFile(daily_zip_file_path)
        for zipped_xml_name in input_zip.namelist():  # LIST ARCHIVES IN ZIP
            try:
                zipped_xml = ZipFile(BytesIO(input_zip.read(zipped_xml_name)))
                # SUPPOSED ONLY ONE XML BUT ITERATE TO BE SURE
                for xml in zipped_xml.namelist():
                    ############################################################
                    # XML PARSER
                    tree = ElementTree.parse(BytesIO(zipped_xml.open(xml).read()))
                    root = tree.getroot()
                    ############################################################
                    # XML RELATED VARIABLES
                    acc_type, siren, year = (None,) * 3
                    identity_writen = False
                    ############################################################
                    # ITERATE ALL TAGS
                    for child in root[0]:
                        ########################################################
                        # IDENTITY TAGS, SIREN AND TYPE OF ACCOUNTABILITY
                        if child.tag == "{fr:inpi:odrncs:bilansSaisisXML}identite":
                            acc_type, siren, denomination, year, ape, \
                            postal_code, town, code_motif, \
                            code_confidentialite, info_traitement = read_identity_data(child, zipped_xml_name)
                            ####################################################
                            # WRITE IDENTITY FILE IF ACCOUNT TYPE IS
                            # KNOWN
                            if acc_type in ACC_ONT.keys():
                                identity_writer.writerow(
                                    (str(siren),
                                     str(denomination),
                                     str(ape),
                                    str(postal_code),
                                     str(town))
                                )
                                identity_writen = True
                        ########################################################
                        # BUNDLE TAGS IN PAGES TO ITERATE WITH BUNDLE CODES
                        # AND AMOUNT
                        elif child.tag == "{fr:inpi:odrncs:bilansSaisisXML}detail":
                            for page in child:
                                for bundle in page:
                                    for bundle_code in \
                                            ACC_ONT[acc_type]['bundleCodeAtt']:
                                        if bundle.attrib.get("code") in bundle_code.keys():
                                            for amount_code in bundle_code[bundle.attrib["code"]]:
                                                amount_code = "m{0}".format(amount_code)
                                                ################################
                                                # WRITE RESULTS FILE
                                                if identity_writen is True and bundle.attrib.get(amount_code):
                                                    bundle_writer.writerow(siren, year,
                                                                           str(CON_ACC[acc_type]),
                                                                           str(CON_BUN[CON_ACC[
                                                                               acc_type]][
                                                                                   bundle.attrib[
                                                                                       "code"]]),
                                                                           str(int(
                                                                               bundle.attrib[
                                                                                   amount_code]
                                                                           )))
            except UnicodeDecodeError as error:
                debug(error)
    except BadZipFile as error:  #  TODO REPORT ERROR TO INPI
        debug(error)

    ############################################################################
    # CLOSES FILES
    bundle_file.close()
    identity_file.close()


def main():
    """
    Based on the configuration storing the input file path. All the xml are
    read to list the bundle code.
    """
    ############################################################################
    # CREATING A LIST OF THE BUNDLE XML CODES, ZIP ARE READ IN BtesIO, IN ORDER
    # TO BREAK FILE SYSTEM. TOO MUCH ZIP DISTURB THE FS.
    for file in listdir(CONFIG['inputPath']):  # LIST INPUT FILES
        if file.endswith(".zip"):  # ONLY PROCESS ZIP FILES
            info("processing INPI daily zip file %s", file)
            process_daily_zip_file(join(CONFIG['inputPath'], file))


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
