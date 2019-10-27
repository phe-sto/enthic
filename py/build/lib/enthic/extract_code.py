# -*- coding: utf-8 -*-
"""
================================================================================
Parse all the XML available to list all the bundle code
================================================================================
"""
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isdir
from os.path import isfile, join

from enthic.utils.configuration import config


def main():
    """Based on the configuration storing the input file path. All the xml are
    read to list the bundle code"""
    ############################################################################
    # CHECKING THE INPUT PATH INCLUDING THE XML TO PARSE
    input_dir = config['inputPath']
    if isdir(input_dir) is False:
        raise NotADirectoryError(
            "Configuration input path {} does not exist".format(input_dir)
        )
    # CHECKING THE RESULT FILE PARAMETER
    result_file = config['codeFile']
    result_file_type = result_file.__class__
    if result_file_type is not str:
        raise TypeError(
            "resultFile parameter must be a string, not {}".format(
                result_file_type
            )
        )
    ############################################################################
    # CREATING A LIST OF THE BUNDLE CODES
    xml_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    with open(result_file, "w")as result_file:  # CODES IN A FILE
        code_list = []
        for xml_file in xml_files:
            tree = ET.parse(join(input_dir, xml_file))
            root = tree.getroot()

            for child in root[0]:
                if child.tag == "{fr:inpi:odrncs:bilansSaisisXML}identite":
                    for _ in child:  # identite LEVEL
                        pass
                elif child.tag == "{fr:inpi:odrncs:bilansSaisisXML}detail":
                    for page in child:
                        for bundle in page:
                            bundle_code = bundle.attrib["code"]
                            if bundle_code in code_list:
                                pass  # CODE ALREADY IN THE LIST
                            else:
                                code_list.append(bundle_code)  # ADD CODE
                                result_file.write('{0};\n'.format(bundle_code))


if __name__ == '__main__':
    main()
