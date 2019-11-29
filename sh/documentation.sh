#!/bin/sh
################################################################################
# PROGRAM BY PAPIT SASU, GENERATE THE DOCUMENTION VIA SPHINX
################################################################################
# 1) CHANGE WORKING DIRECTORY TO py
################################################################################
cd ../python/ || exit;
################################################################################
# 2) BUILD HTML FULL DOCUMENTATION
make html
################################################################################
# 3) COPY HTML BUILD TO STATIC
cp -r build/html/. enthic/static/documentation