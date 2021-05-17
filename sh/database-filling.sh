#!/bin/sh
################################################################################
# FILL THE MySQL DATABASE
################################################################################
# CONSTANTS
readonly SQL_DIR="../sql/";
readonly DATA_DIR="../output";

################################################################################
# COPYING FILE TO A PATH ACCEPTED BY MYSQL SERVER
cp ${DATA_DIR}/bundle.tmp /var/lib/mysql/bundle.csv
cp ${DATA_DIR}/identity.tmp /var/lib/mysql/identity.csv
cp ${DATA_DIR}/metadata.csv /var/lib/mysql/metadata.csv
################################################################################
# INSERT DATA INTO IDENTITY TABLE
mysql enthic < ${SQL_DIR}insert-identity.sql --password="$1" || echo "error when filling table identity"
################################################################################
# INSERT DATA INTO BUNDLE TABLE
mysql enthic < ${SQL_DIR}insert-bundle.sql --password="$1" || echo "error when filling table bundle"
################################################################################
# INSERT DATA INTO METADATA TABLE
mysql enthic < ${SQL_DIR}insert-metadata.sql --password="$1" || echo "error when filling table metadata"
