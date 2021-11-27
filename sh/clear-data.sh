#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CLEAN AND UNZIP INPI DATA
################################################################################
# CONSTANTS
readonly DATA_DIR=$(jq -r .inputPath "../python/enthic/configuration.json");
################################################################################
# VARIABLES
step_count=0;
################################################################################
# FUNCTION
step () {
    # PRINT OUT A STEP NUMBER AND A DESCRIPTION OF THIS SHELL STEP PASSED AS
    # FIRST ARGUMENT.
    step_count=$((step_count+1));      # STEP NUMBER INCREMENT
    printf "STEP %s: %s\n" "$step_count" "$1"; # PRINT STEP AND DESCRIPTION
};
################################################################################
step "REMOVE UNNECESSARY MD5 FILES IN ${DATA_DIR}";
rm -rf $DATA_DIR/*.md5>/dev/null 2>&1;
rm -rf ../output/*.tmp>/dev/null 2>&1;
################################################################################
# CONSIDERED AS TWO STEPS
step "PROCESSING INPI DAILY ZIP FILE IN ${DATA_DIR}";
python3 ../python/enthic/extract_bundle.py
rm -rf $DATA_DIR/*.zip>/dev/null 2>&1;         # DELETE THE UNZIPPED FILE
