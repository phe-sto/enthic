#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
################################################################################
# 1) CREATE A DATABASE AFTER DROP IT IF EXIST
mysql < ${SQL_DIR}create-database-enthic.sql --password="$1";
mysqlCommandResult=$?
if [ $mysqlCommandResult != 0 ]
then
  echo "database creation error : are you using the correct database user, and have you provided the correct password through --password argument ?"
  exit
fi

################################################################################
# 2) CREATE A TABLE OF THE IDENTITY INFORMATION
mysql enthic < ${SQL_DIR}create-table-identity.sql --password="$1" || echo "error when creating table identity"
################################################################################
# 3) CREATE AN HISTORIC FOR BUNDLE TABLE siren COLUMN REQUESTS
mysql enthic < ${SQL_DIR}create-table-request.sql --password="$1" || echo "error when creating table request"
################################################################################
# 4) INSERT DATA INTO IDENTITY TABLE
mysql enthic < ${SQL_DIR}insert-identity.sql --password="$1" || echo "error when filling table identity"
################################################################################
# 5) CREATE A TABLE OF THE BUNDLE INFORMATION
mysql enthic < ${SQL_DIR}create-table-bundle.sql --password="$1" || echo "error when creating table bundle"
################################################################################
# 6) INSERT DATA INTO BUNDLE TABLE
mysql enthic < ${SQL_DIR}insert-bundle.sql --password="$1" || echo "error when filling table bundle"
################################################################################
# 7) CREATE AN FOR IDENTITY TABLE denomination COLUMN
mysql enthic < ${SQL_DIR}create-index-identity.sql --password="$1";
################################################################################
# 8) CREATE AN FOR BUNDLE TABLE siren COLUMN
mysql enthic < ${SQL_DIR}create-index-bundle.sql --password="$1";
################################################################################
# 9) CREATE A TABLE OF THE METADATA INFORMATION
mysql enthic < ${SQL_DIR}create-table-metadata.sql --password="$1";
################################################################################
#10) INSERT DATA INTO METADATA TABLE
mysql enthic < ${SQL_DIR}insert-metadata.sql --password="$1";
#11) CREATE A TABLE FOR SCORING COMPUTATION
mysql enthic < ${SQL_DIR}create-table-statistics.sql --password="$1";
