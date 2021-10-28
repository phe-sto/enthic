#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, CREATE THE MySQL DATABASE
################################################################################

# Move to script directory
script_dir=$(dirname "$0")
cd "${script_dir}" || { echo "Couldn't cd to ${script_dir}"; exit 1; }

# Create mandatory folder if they don't exist
mkdir -p ../input
mkdir -p ../output

# Start downloading and importing data
python3 ../python/enthic/scraping/download_from_INPI.py --source CQuest
