#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# CONSTANTS
readonly PYTHON="python3";
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get -y install zip libxml2-utils mysql-server tree libmysqlclient-dev
################################################################################
# 2) INSTALL DISTANT PACKAGE
python3 -m pip install pytest Sphinx==1.8.5 wheel setuptools sphinx_bootstrap_theme Flask-MySQLdb
################################################################################
# 3) INSTALL ENTHIC PYTHON PACKAGE
sh install-whSuccessfully installed enthic-2019.12.0
eel.sh