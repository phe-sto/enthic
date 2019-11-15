**French societies accountability extraction and treatment by PapIT**
=====================================================================

Project than treat data from opendata-rncs.inpi.fr. They contain xml
files of the account declaration of all french societies. The overall project
is meant to be low-code and open source. Aim to provide ethical indicators on companies.
Information media is a MySQL database, CSV files, web visualisation and a
swagger API. Score and indicators are calculated by batch using fancy libraries.
Scoring, AI, data scrapping for segmentation. Shell and python are to launch be
from their corresponding directory ``./sh`` and ``./py``.

**Install dependencies and python package**
-------------------------------------------

Synaptic packages have to be installed ``zip libxml2-utils mysql-server tree python3``.
Pip packages as well has to be installed for development purpose.

.. code-block:: bash

   $ sh ./install-dependencies.sh

To install the enthic python package only.

.. code-block:: bash

   $ sh ./install-wheel.sh

**Run an instance**
-------------------

Extract data from zip
---------------------

Data are stored in zip files on opendata-rncs.inpi.fr, group by month. Each XML
is in a zip. The first step is then to extract the XML files.

.. code-block:: bash

   $ sh ./clear-data.sh

Check the XML format
--------------------

An XSD is provided by the INPI. This step verify all the XML are following this
XSD. XML not following this XSD have their filename printed out.

.. code-block:: bash

   $ sh ./check-data.sh

Format XML
----------

Create two CSV based on XML. One for each table, the identity and the bundles of
the company.

.. code-block:: bash

   $ sh ./xml-csv.sh

Create MySQL database
---------------------

Create database, tables and indexes. The content of the two tables come from the
previous CSV files.

.. code-block:: bash

   $ sh ./database-creation.sh

Run API
-------

A flask REST API can distribute data over the web. Following Swagger standard.

.. code-block:: bash

   $ python3 ./app.py

**Development and contribution**
----------------------------------

Development and Coding Rules
------------------------------

- snake_case for variables, defintion and CamelCase for classes.
- Only argument is configuration file for python.
- No output or print information (just raw results authorized), just log and files.
- Sonar Qube integration.
- Pytest python and API testing.
- Autodocumentation using Sphinx 1.8.5.
- Benchmark of CPython VS Pypy.
- Common sens and clean code.

Build and install python enthic package
---------------------------------------

.. code-block:: bash

   $ sh ./install-wheel.sh

Testing
-------

Only python package is tested. Used test framework is pytest. Tests can be run
via ``pytest`` in the ``python/enthic/`` directory.


Generate documentation
----------------------

Generate HTML documentation via Sphinx documentation framework.

.. code-block:: bash

   $ sh ./documentation.sh

Library structure
-----------------

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
   ├── python
   │   ├── source
   │   │   ├── conf.py
   │   │   ├── index.rst
   │   │   └── papit.png
   │   │
   │   ├── enthic
   │   │   ├── app.py
   │   │   ├── conftest.py
   │   │   ├── extract_bundle.py
   │   │   ├── __init__.py
   │   │   ├── sum_bundle.py
   │   │   ├── test_extract_bundle.py
   │   │   ├── test_app.py
   │   │   ├── test_sum_bundle.py
   │   │   └── utils
   │   │       ├── configuration.py
   │   │       ├── json_response.py
   │   │       ├── error_json_response.py
   │   │       ├── ok_json_response.py
   │   │       ├── sql_json_response.py
   │   │       └── __init__.py
   │   │
   │   ├── static
   │   │   ├── 404.html
   │   │   ├── 500.html
   │   │   ├── bootstrap.min.css
   │   │   ├── favicon.png
   │   │   ├── index.html
   │   │   ├── jquery.min.js
   │   │   ├── swagger.json
   │   │   ├── swagger-ui-bundle.js
   │   │   ├── swagger-ui-bundle.js.map
   │   │   ├── swagger-ui.css
   │   │   ├── swagger-ui.css.map
   │   │   ├── swagger-ui.js
   │   │   ├── swagger-ui.js.map
   │   │   ├── swagger-ui-standalone-preset.js
   │   │   └── swagger-ui-standalone-preset.js.map
   │   │
   │   ├── setup.py
   │   └── Makefile
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
   ├── sh
   │   ├── check-data.sh   
   │   ├── clear-data.sh
   │   ├── database-creation.sh
   │   ├── documentation.sh
   │   ├── install-dependencies.sh
   │   ├── install-wheel.sh
   │   └── xml-csv.sh
   │
   ├── input
   │   └── qualification
   │       └──...
   │
   └── output


Donation
--------

You can donate to support Python and Open Source development.

**BTC** ``32JSkGXcBK2dirP6U4vCx9YHHjV5iSYb1G``

**ETH** ``0xF556505d13aC9a820116d43c29dc61417d3aB2F8``
