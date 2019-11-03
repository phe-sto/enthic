#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, VERIFY XML XSD CONFORMITY
################################################################################
# CONSTANTS
readonly DATA_DIR="../input/qualification/";
readonly XSD="../bilans-saisis-v1.1.xsd";
readonly STEP_SEP="#";
################################################################################
# PRINT A COMMAND DESCRIPTION
printf "\nCOMPARE ALL %s XML CONFORMITY TO %s\n" "$DATA_DIR" "$XSD";
for xml_file in "$DATA_DIR"/*.xml;                 # ITERATE ALL XML INPUT FILES
    # CHECK WITH XMLLINT WITHOUT OUTPUT (--noout) AND DEVNULL
    do xmllint --noout --schema  $XSD "$xml_file" > /dev/null 2>&1 || \
        printf "%s CHECK FAILED\n" "$xml_file";      # PRINT FAILED CHECK
done;