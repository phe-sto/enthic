################################################################################
# PROGRAM BY PAPIT SASU, EXTRACT XML TO A CSV
################################################################################
# CONSTANTS
readonly OUPUT_DIR="../output/";
# 1) EXECUTE IT PYTHON STEP FROM py FOLDER
cd ../py
################################################################################
# 2) PYTHON STEP THAT EXTRACT ALL BUNDLE AND ALL IDENTITY INFORMATION
../python3_venv/bin/python3 enthic/extract_bundle.py -c ../configuration.json
################################################################################
# 3) SORT THE IDENTITY FILE TO A FINAL CSV FILE
sort ${OUPUT_DIR}identity.tmp > ${OUPUT_DIR}identity.csv
################################################################################
# 4) SORT TO SUM ALL AMOUNT FOR A SOCIETY, A BUNDLE IN A GIVEN YEAR
sort ${OUPUT_DIR}bundle.tmp > ${OUPUT_DIR}sort-bundle.tmp
################################################################################
# 5) PYTHON STEP SUM A BUNDLE OF A COMPANY FOR A GIVEN YEAR
../python3_venv/bin/python3 enthic/sum_bundle.py -c ../configuration.json > ${OUPUT_DIR}bundle.csv