#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, INSTALL THE REQUIRED DEPENDENCIES
################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get -y install libxml2-utils mariadb-server tree libmariadbclient-dev python3-pip
################################################################################
# 2) RUN MARIADB SERVER SECURISATION
mysql_secure_installation
################################################################################
# 3) INSTALL DISTANT PACKAGE
python3 -m pip install pytest sphinx wheel setuptools numpy wget py7zr sqlalchemy pymysql
################################################################################
# 4) INSTALL ENTHIC PYTHON PACKAGE
sh install-wheel.sh
