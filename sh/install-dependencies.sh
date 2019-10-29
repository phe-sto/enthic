#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get install zip libxml2-utils mysql-server
################################################################################
# 2) CHANGE WORKING DIRECTORY TO PYTHON FOLDER
cd ../py
################################################################################
# 3) INSTALL LOCAL PYTHON PACKAGE
../python3_venv/bin/python3 enthic/extract_bundle.py -c ../configuration.json