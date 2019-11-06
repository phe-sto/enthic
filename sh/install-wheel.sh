#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, EXTRACT XML TO A CSV
################################################################################
# CONSTANTS
readonly DIST="dist/";
readonly PYTHON="python3";
################################################################################
# 1) EXECUTE IT PYTHON STEP FROM py FOLDER
cd ../python || exit;
################################################################################
# 2) REMOVE dist DIRCTORY
rm -rf $DIST
################################################################################
# 3) BUILD THE wheel
$PYTHON setup.py bdist_wheel
################################################################################
# 4) INSTALL FROM dist DIRECTORY
cd $DIST || exit;
################################################################################
# 5) UNINSTALL POSSIBLY INSTAL enthic PACKAGE
$PYTHON -m pip uninstall enthic -y
################################################################################
# 6) INSTALL FORMERLY CREATED enthic wheel
$PYTHON -m pip install enthic-0.1-py3-none-any.whl