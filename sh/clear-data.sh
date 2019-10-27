#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CLEAN AND UNZIP INPI DATA
################################################################################
# CONSTANTS
readonly DATA_DIR="../input/";
readonly STEP_SEP="#";
################################################################################
# VARIABLES
step_count=0;
################################################################################
# FUNCTION
step () {
    # PRINT OUT A STEP NUMBER AND A DESCRIPTION OF THIS SHELL STEP PASSED AS
    # FIRST ARGUMENT.
    step_count=$(($step_count+1));      # STEP NUMBER INCREMENT
    printf %80s | tr " " "$STEP_SEP";   # PRINT OUT A STEP SPEARATOR
    printf "\nSTEP $step_count: $1\n";  # PRINT OUT STEP NUMBER AND DESCRIPTION
};
################################################################################
step "REMOVE UNNECESSARY MD5 FILES IN $DATA_DIR";
rm -rf $DATA_DIR*.md5;
################################################################################
for unzipping_step in "DAILY" "DECLARATION";    # ZIP CONTAINS ZIP, DO IT TWICE
do  
    # CONSIDERED AS TWO STEPS
    step "UNZIP $unzipping_step ZIP IN $DATA_DIR";
    for zip_file in $DATA_DIR*.zip;             # ITERATE ALL INPUT FILES
    do
        unzip -o -qq $zip_file -d $DATA_DIR;    # UNZIP
        rm $zip_file;                           # DELETE THE UNZIPPED FILE
    done;
done;