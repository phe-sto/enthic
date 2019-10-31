French society accountability extraction and treatment by PapIT
###############################################################

Project than treat data from opendata-rncs.inpi.fr. They contain xml
files of the account declaration of all french societies. The overall project
is meant to be a low-code one. Aim to provide ethical indicators on companies.
Information media is a MySQL database, CSV files, web visualisation and a
swagger API. Score and indicators are calculated by batch using fancy libraries.
Scoring, AI, data scrapping for segmentation.

Developpement and Coding Rules
==============================

- Snake case for variables.
- Only argument is configuration file for python.
- No output or print, just log and files.
- Sonar Qube integration.
- Pytest python and API testing.
- Autodocumentation using Sphinx 1.8.5.
- Benchmark of CPython and Pypy.

Install dependencies
====================

Interpreter and VM for python are embedded is the project code for benchmarking
purpose. Synaptic packages have to be installed. Pip packages as well has to be
installed.

.. code-block:: bash

   $ sh ./install-dependencies.sh

Extract data from zip
=====================

Data are stored in zip files on opendata-rncs.inpi.fr, group by month. Each XML
is in a zip. The first step is then to extract the XML files.

.. code-block:: bash

   $ sh ./clear-data.sh

Check the XML format
====================

An XSD is provided by the INPI. This step verify all the XML are following this
XSD. XML not following this XSD have their filename printed out.

.. code-block:: bash

   $ sh ./check-data.sh

Format XML
==========

Create two CSV based on XML. One for each table, the identity and the bundles of
the company.

.. code-block:: bash

   $ sh ./xml-csv.sh

Create MySQL database
=====================

Create database, tables and indexes. The content of the two tables come from the
previous CSV files.

.. code-block:: bash

   $ sh ./database-creation.sh

Documentation generation and testing
====================================

The open project aim to be open source and well documented. Nevertheless the
test running and documentation generation will not be detailed here and be left
to eventual contributor appreciation.

Library structure
=================

.. code-block:: bash

   .
   │
   ├── configuration.json
   ├── bilans-saisis-v1.1.xsd
   ├── sonar-project.properties
   ├── README.rst
   ├── account-ontology.csv
   ├── .gitignore
   │
   ├── py
   │   ├── enthic
   │   │   ├── conftest.py
   │   │   ├── extract_bundle.py
   │   │   ├── __init__.py
   │   │   ├── sum_bundle.py
   │   │   ├── test_extract_bundle.py
   │   │   ├── test_sum_bundle.py
   │   │   └── utils
   │   │       ├── configuration.py
   │   │       └── __init__.py
   │   │
   │   └── setup.py
   │
   ├── sql
   │   ├── create-database-enthic.sql
   │   ├── create-index-bundle.sql
   │   ├── create-index-identity.sql
   │   ├── create-table-bundle.sql 
   │   ├── create-table-identity.sql
   │   ├── insert-bundle.sql
   │   └── insert-identity.sql   
   │
   ├── python3_venv
   │   └──...
   │
   ├── pypy3.6-v7.1.1-linux64
   │   └──...
   │
   ├── sh
   │   ├── check-data.sh   
   │   ├── clear-data.sh
   │   ├── database-creation.sh
   │   ├── install-dependencies.sh
   │   └── xml-csv.sh
   │
   ├── input
   │   └── qualification
   └── output


Donation
========

You can donate to support Python and Open Source development.

**BTC** ``32JSkGXcBK2dirP6U4vCx9YHHjV5iSYb1G``

**ETH** ``0xF556505d13aC9a820116d43c29dc61417d3aB2F8``