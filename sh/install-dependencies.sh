#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get -y install libxml2-utils mysql-server tree libmysqlclient-dev python3-pip
################################################################################
# 2) INSTALL DISTANT PACKAGE
python3 -m pip install pytest sphinx wheel setuptools
################################################################################
# 3) INSTALL ENTHIC PYTHON PACKAGE
sh install-wheel.sh
