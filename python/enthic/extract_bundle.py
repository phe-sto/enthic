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
from csv import reader
from enum import Enum, auto
from io import BytesIO
from json import load
from logging import info, debug, basicConfig
from os import listdir
from os.path import dirname, join, isdir
from re import sub, compile
from zipfile import ZipFile, BadZipFile
from enthic.ontology import ONTOLOGY

from enthic.utils.conversion import CON_APE, CON_ACC, CON_BUN


class ModifiedData(Enum):
    """Enum used to replace or insert data in CSV"""
    ABSENT = auto()
    WRONG_FORMAT = auto()


RE_DENOMINATION = compile(r'\s+|[\t\n]')  # NOT AN OBVIOUS PERFORMANCE GAIN...
RE_POSTAL_CODE_TOWN = compile(r"([0-9]+)[ -]?([a-zA-Z0-9_ \'\"-\.\(\)\-]+)")
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

################################################################################
# Usin ONTOLOGY at the place of account-ontology.csv
code =  {'FW': 3,
        'GU': 3,
        '242': 1,
        '262': 1,
        'FY': 3,
        '252': 1,
        'FP': 3,
        'FV': 3,
        'GV': 3,
        '378': 1,
        '376': 1,
        'XQ': 1,
        '306': 1,
        'HI': 1,
        'HF': 1,
        'R7': 1,
        'R6': 1,
        '210': 1,
        '290': 1,
        'R8': 1,
        '316': 1,
        'R2': 1,
        '280': 1,
        '270': 1,
        'FA': 3,
        'FO': 3,
        '215': 1,
        'FR': 3,
        '9Z': 1,
        'FM': 3,
        'GD': 3,
        'GO': 3,
        'YT': 1,
        'GA': 3,
        '243': 1,
        'FX': 3,
        'YU': 1,
        'GI': 3,
        '236': 1,
        'SS': 1,
        '209': 1,
        'R5': 1,
        'GP': 3,
        'GL': 3,
        '256': 1,
        'GT': 3,
        'FN': 3,
        'FU': 3,
        'GB': 3,
        'HE': 1,
        '226': 1,
        '250': 1,
        'HH': 1,
        'R4': 1,
        'HB': 1,
        '230': 1,
        '238': 1,
        '217': 1,
        '218': 1,
        'HK': 1,
        '232': 1,
        'HC': 1,
        'FJ': 3,
        'YW': 1,
        '214': 1,
        '310': 1,
        '234': 1,
        'YY': 1,
        'ZE': 1,
        'FQ': 3,
        '264': 1,
        '259': 1,
        'R1': 1,
        '300': 1,
        'GK': 3,
        'HN': 1,
        'FD': 3,
        'FT': 3,
        'GJ': 3,
        'GG': 3,
        '240': 1,
        'YZ': 1,
        'GR': 3,
        'GH': 3,
        'HD': 1,
        'GW': 3,
        'YP': 1,
        'R3': 1,
        '224': 1,
        'GN': 3,
        'FZ': 3,
        'HL': 1,
        'FS': 3,
        'HG': 1,
        '244': 1,
        'HM': 1,
        'YV': 1,
        'GM': 3,
        'GS': 3,
        'HA': 1,
        'GE': 3,
        'GQ': 3,
        'HJ': 1,
        '254': 1,
        'GC': 3,
        'FG': 3,
        'GF': 3,
        '222': 1,
        '294': 1,
        '374': 1
        }

ACCOUNTING = ONTOLOGY['accounting']
ACC_ONT = dict() # EMPTY OBJECT STORING DATA TO EXTRACT
for key in ACCOUNTING:
    ACC_ONT[ACCOUNTING[key][0]] = {"bundleCodeAtt":[]}
    for y in ACCOUNTING[key]['code']:
        try:
            ACC_ONT[ACCOUNTING[key][0]]["bundleCodeAtt"].append(
                {ACCOUNTING[key]['code'][y][0]: str(code[ACCOUNTING[key]['code'][y][0]]).split(",")}
            )
        except KeyError:
            continue

################################################################################
# SET LOG LEVEL
basicConfig(level=CONFIG['debugLevel'],
            format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")


def read_identity_data(identity_xml_item):
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
            code_motif = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_confidentialite':
            code_confidentialite = identity.text
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}info_traitement':
            info_traitement = identity.text if identity.text else ModifiedData.ABSENT.value
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}date_cloture_exercice':
            year = identity.text[:4]
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}adresse':
            ####################################################################
            # PARSING THE 'adresse' FIELD, MANY DATA-CAPTURE ERROR.
            try:
                regex_match = RE_POSTAL_CODE_TOWN.match(identity.text)
                postal_code = regex_match.group(1)
                town = regex_match.group(2).upper()
            except TypeError as error:
                debug("{0}: {1}".format(str(error),
                                        str(identity.text)))
                postal_code, town = (ModifiedData.WRONG_FORMAT.value,) * 2
            except AttributeError as error:
                try:
                    debug("{0}: {1}".format(str(error),
                                            str(identity.text)))
                    regex_match = RE_TOWN.match(identity.text)
                    town = regex_match.group(1).upper()
                    postal_code = ModifiedData.WRONG_FORMAT.value
                except AttributeError as error:
                    try:
                        debug(
                            "{0}: {1}".format(str(error),
                                              str(identity.text)))
                        regex_match = RE_POSTAL_CODE.match(identity.text)
                        town = ModifiedData.WRONG_FORMAT.value
                        postal_code = regex_match.group(1)
                    except AttributeError as error:
                        debug(
                            "{0}: {1}".format(str(error),
                                              str(identity.text)))
                        postal_code, town = \
                            (ModifiedData.WRONG_FORMAT.value,) * 2
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_activite':
            try:
                ape = str(CON_APE[identity.text])
            except KeyError:
                ape = 1672

    return acc_type, siren, denomination, year, ape, postal_code, town, \
           code_motif, code_confidentialite, info_traitement


def main():
    """
    Based on the configuration storing the input file path. All the xml are
    read to list the bundle code.
    """

    ############################################################################
    # CREATING THE OUTPUT FILES FOR RESULT AND IDENTITY
    bundle_file = open(join(CONFIG['outputPath'], CONFIG['tmpBundleFile']), "a")
    identity_file = open(join(CONFIG['outputPath'], CONFIG['identityFile']), "a")
    metadata_file = open(join(CONFIG['outputPath'], CONFIG['metadataFile']), "a")
    ############################################################################
    # CREATING A LIST OF THE BUNDLE XML CODES, ZIP ARE READ IN BtesIO, IN ORDER
    # TO BREAK FILE SYSTEM. TOO MUCH ZIP DISTURB THE FS.
    for file in listdir(CONFIG['inputPath']):  # LIST INPUT FILES
        info("processing INPI daily zip file %s", file)
        if file.endswith(".zip"):  # ON RETAIN ZIP FILES
            try:  # SOME BAD ZIP FILE ARE IN HE DATASET
                input_zip = ZipFile(join(CONFIG['inputPath'], file))
                for zipped_xml in input_zip.namelist():  # LIST ARCHIVES IN ZIP
                    try:
                        zipped_xml = ZipFile(BytesIO(input_zip.read(zipped_xml)))
                        # SUPPOSED ONLY ONE XML BUT ITERATE TO BE SURE
                        for xml in zipped_xml.namelist():
                            ####################################################
                            # XML PARSER
                            tree = ElementTree.parse(BytesIO(zipped_xml.open(xml).read()))
                            root = tree.getroot()
                            ####################################################
                            # XML RELATED VARIABLES
                            acc_type, siren, year = (None,) * 3
                            identity_writen = False
                            ####################################################
                            # ITERATE ALL TAGS
                            for child in root[0]:
                                ################################################
                                # IDENTITY TAGS, SIREN AND TYPE OF ACCOUNTABILITY
                                if child.tag == "{fr:inpi:odrncs:bilansSaisisXML}identite":
                                    acc_type, siren, denomination, year, ape, \
                                    postal_code, town, code_motif, \
                                    code_confidentialite, info_traitement = read_identity_data(child)
                                    ############################################
                                    # WRITE IDENTITY FILE IF ACCOUNT TYPE IS
                                    # KNOWN
                                    if acc_type in ACC_ONT.keys():
                                        identity_file.write(
                                            "\t".join(
                                                (str(siren), str(denomination), str(ape),
                                                 str(postal_code), str(town), "\n")))
                                        identity_writen = True
                                        metadata_file.write(
                                            "\t".join(
                                                (str(siren), str(year), str(code_motif),
                                                 str(code_confidentialite), str(info_traitement), "\n")))
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
                                                            ####################
                                                            # WRITE RESULTS FILE
                                                            if identity_writen is True:
                                                                bundle_file.write(
                                                                    "\t".join((siren, year,
                                                                               str(CON_ACC[acc_type]),
                                                                               str(CON_BUN[CON_ACC[
                                                                                   acc_type]][
                                                                                       bundle.attrib[
                                                                                           "code"]]),
                                                                               str(int(
                                                                                   bundle.attrib[
                                                                                       amount_code]
                                                                               )),
                                                                               "\n")))
                                            except KeyError as key_error:
                                                debug("{} in account {} bundle {}".format(
                                                    key_error,
                                                    acc_type,
                                                    bundle.attrib[
                                                        "code"]
                                                ))
                    except UnicodeDecodeError as error:
                        debug(error)
            except BadZipFile as error:  #  TODO REPORT ERROR TO INPI
                debug(error)
    ############################################################################
    # CLOSES RESULTS AND IDENTITY FILES
    bundle_file.close()
    identity_file.close()
    metadata_file.close()


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
