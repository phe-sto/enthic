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
from io import BytesIO
from json import load
from logging import info, debug, basicConfig
from os import listdir
from os.path import dirname, join, isdir
from re import sub, compile
from zipfile import ZipFile, BadZipFile

from enthic.utils.conversion import CON_APE, CON_ACC, CON_BUN

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

def read_identity_data(identity_xml_item):
    """
    Read the xml's identity item, to extract useful data from it

       :param identity_xml_item: the identity XMl object
       :return: extracted data as a tuple
    """
    acc_type, siren, denomination, year, ape, \
    postal_code, town, code_motif, \
    code_confidentialite, info_traitement = (None,) * 10

    # -1 is defined as default value in CODE_CONFIDENTIALITE in ontology.py
    code_confidentialite = "-1"

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
            info_traitement = identity.text if identity.text else "rien"
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}date_cloture_exercice':
            year = identity.text[:4]
        elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}adresse':
            ####################################
            # PARSING THE 'adresse' FIELD, MANY DATA-CAPTURE ERROR.
            try:
                regex_match = RE_POSTAL_CODE_TOWN.match(identity.text)
                postal_code = regex_match.group(1)
                town = regex_match.group(2).upper()
            except TypeError as error:
                debug("{0}: {1}".format(str(error),
                                        str(identity.text)))
                postal_code, town = ('INCOG',) * 2
            except AttributeError as error:
                try:
                    debug("{0}: {1}".format(str(error),
                                            str(identity.text)))
                    regex_match = RE_TOWN.match(identity.text)
                    town = regex_match.group(1).upper()
                    postal_code = 'INCOG'
                except AttributeError as error:
                    try:
                        debug(
                            "{0}: {1}".format(str(error),
                                              str(identity.text)))
                        regex_match = RE_POSTAL_CODE.match(identity.text)
                        town = 'INCOG'
                        postal_code = regex_match.group(1)
                    except AttributeError as error:
                        debug(
                            "{0}: {1}".format(str(error),
                                              str(identity.text)))
                        postal_code, town = ('INCOG',) * 2
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
                                                (siren, denomination, str(ape),
                                                 postal_code, town, "\n")))
                                        identity_writen = True
                                        metadata_file.write(
                                            "\t".join(
                                                (siren, year, code_motif, code_confidentialite, info_traitement, "\n")))
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
                        debug(key_error)
            except BadZipFile as error:  #  TODO REPORT ERROR TO INPI
                debug(error)
    ############################################################################
    # CLOSES RESULTS AND IDENTITY FILES
    bundle_file.close()
    identity_file.close()
    metadata_file.close()

if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
