#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, VERIFY XML XSD CONFORMITY
################################################################################
# CONSTANTS
readonly DATA_DIR="../input/";
readonly XSD="../bilans-saisis-v1.1.xsd";
readonly STEP_SEP="#";
################################################################################
printf %80s | tr " " "$STEP_SEP";               # PRINT OUT A STEP SPEARATOR
# PRINT A COMMAND DESCRIPTION
printf "\nCOMPARE ALL $DATA_DIR XML CONFORMITY TO $XSD\n";
for xml_file in $DATA_DIR*.xml;                 # ITERATE ALL XML INPUT FILES
    # CHECK WITH XMLLINT WITHOUT OUTPUT (--noout) AND DEVNULL
    do xmllint --noout --schema  $XSD $xml_file > /dev/null 2>&1 || \
        printf "$xml_file CHECK FAILED\n";      # PRINT FAILED CHECK
done;