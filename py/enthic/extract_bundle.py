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
from logging import debug, basicConfig
from os import listdir
from os.path import isdir, isfile, join
from re import sub, compile

re_multiple_whitespace = compile(r"\s+")  # NOT AN OBVIOUS PERFORMANCE GAIN...


def main():
    """
    Based on the configuration storing the input file path. All the xml are
    read to list the bundle code.
    """
    from enthic.utils.configuration import config  # UGLY, FOR SPHINX IMPORT
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
    basicConfig(level=config['debugLevel'], format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    ############################################################################
    # READ THE CODES TO EXTRACT
    account_ontology = {}  # EMPTY OBJECT STORING DATA TO EXTRACT
    with open(config['accountOntologyCSV'], mode='r') as infile:
        _reader = reader(infile, delimiter=';')
        next(_reader, None)  # SKIP FIRST LINE, HEADER OF THE CSV
        for rows in _reader:  # ITERATES ALL THE LINES
            try:
                account_ontology[rows[3]]["bundleCodeAtt"].append(
                    {rows[1]: rows[2].split(",")}
                )
            except KeyError:
                account_ontology[rows[3]] = {"bundleCodeAtt": []}
    ############################################################################
    # CREATING A LIST OF THE BUNDLE CODES
    xml_files = [f for f in listdir(config['inputPath']) if
                 isfile(join(config['inputPath'], f))]
    ############################################################################
    # CREATING THE OUTPUT FILES FOR RESULT AND IDENTITY
    bundle_file = open(join(config['outputPath'], config['bundleFile']), "w")
    identity_file = open(join(config['outputPath'], config['identityFile']), "w")
    ############################################################################
    # ITERATE ALL XML FILES
    for xml_file in xml_files:
        ########################################################################
        # XML PARSER
        tree = ElementTree.parse(join(config['inputPath'], xml_file))
        root = tree.getroot()
        ########################################################################
        # XML RELATED VARIABLES
        accountability_type, siren, code_devise, denomination, year = (None,) * 5
        ########################################################################
        # ITERATE ALL TAGS
        for child in root[0]:
            ####################################################################
            # IDENTITY TAGS, SIREN AND TYPE OF ACCOUNTABILITY
            if child.tag == "{fr:inpi:odrncs:bilansSaisisXML}identite":
                for identity in child:  # identite LEVEL
                    if identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}siren':
                        siren = identity.text
                    elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_type_bilan':
                        accountability_type = identity.text
                    elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}denomination':
                        # REMOVE MULTIPLE WHITESPACES, SWITCH TO UPPER CASE, REMOVE EOF
                        denomination = sub(re_multiple_whitespace, " ",
                                           identity.text.replace("\n", " ").upper()
                                           ).strip(" ")
                    elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}code_devise':
                        code_devise = identity.text
                    elif identity.tag == '{fr:inpi:odrncs:bilansSaisisXML}date_cloture_exercice':
                        year = identity.text[:4]
                ################################################################
                # WRITE IDENTITY FILE
                identity_file.write(";".join([siren, denomination,
                                              accountability_type, code_devise,
                                              "\n"]))
            ####################################################################
            # BUNDLE TAGS IN PAGES TO ITERATE WITH BUNDLE CODES AND AMOUNT
            elif child.tag == "{fr:inpi:odrncs:bilansSaisisXML}detail":
                for page in child:
                    for bundle in page:
                        try:
                            for bundle_code in \
                                    account_ontology[accountability_type]['bundleCodeAtt']:
                                if bundle.attrib["code"] in bundle_code.keys():
                                    for amount_code in bundle_code[bundle.attrib["code"]]:
                                        amount_code = "m{0}".format(amount_code)
                                        ########################################
                                        # WRITE RESULTS FILE
                                        bundle_file.write(";".join([siren, year,
                                                                    bundle.attrib["code"],
                                                                    str(int(bundle.attrib[amount_code])),
                                                                    "\n"]))
                        except KeyError as key_error:
                            debug(key_error)
    ############################################################################
    # CLOSES RESULTS AND IDENTITY FILES
    bundle_file.close()
    identity_file.close()


if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
