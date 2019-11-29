#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
################################################################################
# 1) CREATE A DATABASE AFTER DROP IT IF EXIST
mysql < ${SQL_DIR}create-database-enthic.sql "$1";
################################################################################
# 2) CREATE A TABLE OF THE IDENTITY INFORMATION
mysql enthic < ${SQL_DIR}create-table-identity.sql "$1";
################################################################################
# 3) CREATE AN FOR BUNDLE TABLE siren COLUMN
mysql enthic < ${SQL_DIR}create-table-request.sql "$1";
################################################################################
# 4) INSERT DATA INTO IDNETITY TABLE
mysql enthic < ${SQL_DIR}insert-identity.sql "$1";
################################################################################
# 5) CREATE A TABLE OF THE BUNDLE INFORMATION
mysql enthic < ${SQL_DIR}create-table-bundle.sql "$1";
################################################################################
# 6) INSERT DATA INTO BUNDLE TABLE
mysql enthic < ${SQL_DIR}insert-bundle.sql "$1";
################################################################################
# 7) CREATE AN FOR IDENTITY TABLE denomination COLUMN
mysql enthic < ${SQL_DIR}create-index-identity.sql "$1";
################################################################################
# 8) CREATE AN FOR BUNDLE TABLE siren COLUMN
mysql enthic < ${SQL_DIR}create-index-bundle.sql "$1";
