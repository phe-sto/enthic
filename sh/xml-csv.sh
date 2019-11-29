#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, EXTRACT XML TO A CSV
################################################################################
# CONSTANTS
readonly OUPUT_DIR="../output/";
readonly INPUT_DIR="../input/";
# 1) EXECUTE IT PYTHON STEP FROM py FOLDER
cd ../python || exit;
################################################################################
# 2) SORT THE IDENTITY FILE TO A FINAL CSV FILE
sort ${OUPUT_DIR}identity.tmp > ${OUPUT_DIR}identity.csv
################################################################################
# 3) SORT TO SUM ALL AMOUNT FOR A SOCIETY, A BUNDLE IN A GIVEN YEAR
sort ${OUPUT_DIR}bundle.tmp > ${OUPUT_DIR}sort-bundle.tmp
################################################################################
# 4) PYTHON STEP SUM A BUNDLE OF A COMPANY FOR A GIVEN YEAR
python3 enthic/sum_bundle.py -c ../configuration.json > ${OUPUT_DIR}bundle.csv
################################################################################
# 5) CLEAN UP OUTPUT DIRECTY
rm -rf ${OUPUT_DIR}*.tmp;