#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get install zip libxml2-utils mysql-server tree python3
################################################################################
# 2) INSTALL LOCAL PYTHON PACKAGE
python3 setup.py install
################################################################################
# 3) INSTALL DISTANT PACKAGE
python3 -m pip install pytest Sphinx==1.8.5