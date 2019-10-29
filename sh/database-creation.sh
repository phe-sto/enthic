#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
################################################################################
# 1) CREATE A DATABASE AFTER DROP IT IF EXIST
mysql < ${SQL_DIR}create-database-enthic.sql
################################################################################
# 2) CREATE A TABLE OF THE IDENTITY INFORMATION
mysql enthic < ${SQL_DIR}create-table-identity.sql
################################################################################
# 3) INSERT DATA INTO IDNETITY TABLE
mysql enthic < ${SQL_DIR}insert-identity.sql
################################################################################
# 4) CREATE A TABLE OF THE BUNDLE INFORMATION
mysql enthic < ${SQL_DIR}create-table-bundle.sql
################################################################################
# 5) INSERT DATA INTO BUNDLE TABLE
mysql enthic < ${SQL_DIR}insert-bundle.sql
################################################################################
# 6) CREATE TWO INDEXES FOR IDENTITY TABLE
mysql enthic < ${SQL_DIR}create-index-identity.sql
################################################################################
# 7) CREATE AN INDEX FOR BUNDLE TABLE
mysql enthic < ${SQL_DIR}create-index-bundle.sql
