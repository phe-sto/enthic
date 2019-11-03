#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get install zip libxml2-utils mysql-server tree libmysqlclient-dev
################################################################################
# 2) INSTALL DISTANT PACKAGE
python3 -m pip install pytest Sphinx==1.8.5
################################################################################
# 3) NAVIGATE TO PYTHON FOLDER
cd ../py/ || exit;
################################################################################
# 4) INSTALL LOCAL PYTHON PACKAGE
python3 -m pip setup.py install