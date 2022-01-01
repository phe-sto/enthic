#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, EXTRACT XML TO A CSV
################################################################################
# CONSTANTS
readonly CONFIGURATION="../python/enthic/configuration.json";
readonly OUTPUT_DIR=$(jq -r .outputPath $CONFIGURATION);
readonly BUNDLE=$(jq -r .bundleTmpFile $CONFIGURATION);
readonly IDENTITY=$(jq -r .identityTmpFile $CONFIGURATION);
readonly SORT_BUNDLE=$(jq -r .sortBundleTmpFile $CONFIGURATION);
# 1) EXECUTE IT PYTHON STEP FROM py FOLDER
cd ../python || exit;
################################################################################
# 2) SORT THE IDENTITY FILE TO A FINAL CSV FILE
sort "$OUTPUT_DIR$IDENTITY" -uk1,1 -t";" > "${OUTPUT_DIR}identity.csv"
################################################################################
# 3) SORT TO SUM ALL AMOUNT FOR A SOCIETY, A BUNDLE IN A GIVEN YEAR
sort "$OUTPUT_DIR$BUNDLE" > "$OUTPUT_DIR$SORT_BUNDLE"
################################################################################
# 4) PYTHON STEP SUM A BUNDLE OF A COMPANY FOR A GIVEN YEAR
python3 enthic/treat_bundle.py
exit
################################################################################
# 5) MOVE TO LOAD DIRECTORY FOR MYSQL 8 COMPATIBILITY
mv "$OUTPUT_DIR*.csv" /var/lib/mysql
################################################################################
# 6) CLEAN UP OUTPUT DIRECTORY
rm -rf "$OUTPUT_DIR*.tmp";
