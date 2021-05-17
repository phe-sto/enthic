#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
################################################################################
# 1) CREATE A DATABASE AFTER DROP IT IF EXIST
mysql < ${SQL_DIR}create-database-enthic.sql --password="$1" || echo "database creation error : are you using the correct database user, and have you provided the correct password through --password argument ?"

################################################################################
# 2) CREATE A TABLE OF THE IDENTITY INFORMATION
mysql enthic < ${SQL_DIR}create-table-identity.sql --password="$1" || echo "error when creating table identity"
################################################################################
# 3) CREATE AN HISTORIC FOR BUNDLE TABLE siren COLUMN REQUESTS
mysql enthic < ${SQL_DIR}create-table-request.sql --password="$1" || echo "error when creating table request"
################################################################################
# 4) CREATE A TABLE OF THE BUNDLE INFORMATION
mysql enthic < ${SQL_DIR}create-table-bundle.sql --password="$1" || echo "error when creating table bundle"
################################################################################
# 5) CREATE AN INDEX FOR IDENTITY TABLE denomination COLUMN
mysql enthic < ${SQL_DIR}create-index-identity.sql --password="$1";
################################################################################
# 6) CREATE AN INDEX FOR BUNDLE TABLE siren COLUMN
mysql enthic < ${SQL_DIR}create-index-bundle.sql --password="$1";
################################################################################
# 7) CREATE A TABLE OF THE METADATA INFORMATION
mysql enthic < ${SQL_DIR}create-table-metadata.sql --password="$1";
################################################################################
# 8) CREATE A TABLE FOR SCORING COMPUTATION
mysql enthic < ${SQL_DIR}create-table-statistics.sql --password="$1";
# 9) CREATE A TABLE FOR STATISTICS BY APE
mysql enthic < ${SQL_DIR}create-table-ape-stats.sql --password="$1";
################################################################################
#10) INSERT DATA INTO DATABASE
./database-update.sh
