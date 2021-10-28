#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
################################################################################
# 1) CREATE A DATABASE AFTER DROP IT IF EXIST
mysql enthic < ${SQL_DIR}export-database-to-csv.sql --password="$1" || echo "database export error : are you using the correct database user, and have you provided the correct password through --password argument ?"
