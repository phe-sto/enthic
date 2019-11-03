#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, EXTRACT XML TO A CSV
################################################################################
# CONSTANTS
readonly OUPUT_DIR="../output/";
readonly INPUT_DIR="../input/";
# 1) EXECUTE IT PYTHON STEP FROM py FOLDER
cd ../py || exit;
################################################################################
# 2) PYTHON STEP THAT EXTRACT ALL BUNDLE AND ALL IDENTITY INFORMATION
python3 enthic/extract_bundle.py -c ../configuration.json
################################################################################
# 3) SORT THE IDENTITY FILE TO A FINAL CSV FILE
sort ${OUPUT_DIR}identity.tmp > ${OUPUT_DIR}identity.csv
################################################################################
# 4) SORT TO SUM ALL AMOUNT FOR A SOCIETY, A BUNDLE IN A GIVEN YEAR
sort ${OUPUT_DIR}bundle.tmp > ${OUPUT_DIR}sort-bundle.tmp
################################################################################
# 5) PYTHON STEP SUM A BUNDLE OF A COMPANY FOR A GIVEN YEAR
python3 enthic/sum_bundle.py -c ../configuration.json > ${OUPUT_DIR}bundle.csv
################################################################################
# 6) PYTHON STEP SUM A BUNDLE OF A COMPANY FOR A GIVEN YEAR
python3 enthic/sum_bundle.py -c ../configuration.json > ${OUPUT_DIR}bundle.csv
################################################################################
# 7) CLEAN UP INPUT DIRECTY
rm -rf $INPUT_DIR
################################################################################
# 8) CREATE A NEW INPUT DIRECTY
mkdir $INPUT_DIR