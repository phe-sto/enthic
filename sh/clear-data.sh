#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CLEAN AND UNZIP INPI DATA
################################################################################
# CONSTANTS
readonly DATA_DIR="../input";
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
rm -rf $DATA_DIR/*.md5;
rm -rf ../output/*.tmp;
################################################################################
for unzipping_step in "DAILY" "DECLARATION";     # ZIP CONTAINS ZIP, DO IT TWICE
do  
    # CONSIDERED AS TWO STEPS
    step "UNZIP IN PYTHON ${unzipping_step} ZIP IN ${DATA_DIR}";
    for zip_file in "$DATA_DIR"/*.zip;           # ITERATE ALL INPUT FILES
    do
        python3 ../python/enthic/extract_bundle.py -c ../configuration.json
        rm "$zip_file">/dev/null 2>&1;           # DELETE THE UNZIPPED FILE
    done;
done;