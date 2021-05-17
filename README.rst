**French societies accountability extraction and treatment by PapIT**
=====================================================================

Project that treats data from opendata-rncs.inpi.fr. They contain xml
files of the account declaration of all french societies. The overall project
is meant to be low-code and open source. Aim to provide ethical indicators on companies.
Information media is a MySQL database, CSV files, web visualisation and a
swagger API. The search engine endpoint return a JSON-LD (Hydra) compliant JSON.
Company JSON cannot conform to JSON-LD Organization type due to lack of data
(contact for instance).
Score and indicators are calculated by batch, sql and why not using
fancy libraries. Help in data treatment to improve scoring would be appreciated.
Scoring, AI, data scrapping for segmentation. Shell and python must be launched
from their corresponding directory ``./sh`` and ``./py``.

**Install dependencies and python package**
-------------------------------------------

Synaptic packages have to be installed ``libxml2-utils mysql-server tree python3``.
Pip packages as well have to be installed for development purpose.

.. code-block:: bash

   $ sh ./install-dependencies.sh

To install the enthic python package only.

.. code-block:: bash

   $ sh ./install-wheel.sh

**Run an instance**
-------------------

***Fill configuration file***
-----------------------------
Fill file ``python/enthic/configuration.json`` with correct user/password for Mysql and INPI.



***Create MySQL database and fill it***
---------------------------------------
Create database, tables and indexes. Then begins to download data from INPI's FTP and loads it into MySQL database

.. code-block:: bash

   $ sh ./database-creation.sh <your mysql password>

***Run API***
-------------

A flask REST API can distribute data over the web. Following Swagger standard.

.. code-block:: bash

   $ python3 ./app.py

**Development and contribution**
--------------------------------

License
-------

`Do What The Fuck You Want To Public License (WTFPL) <http://www.wtfpl.net/about/>`_

Development and Coding Rules
----------------------------

- snake_case for variables, definition and CamelCase for classes.
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

Generate HTML documentation via Sphinx documentation framework. Sphinx is called
programmatically at the beginning of setup.py. Therefore the above installation
build the doc at the same time.

Library structure
-----------------

.. code-block:: bash

    ./enthic
    ├── account-ontology.csv
    ├── bilans-saisis-v1.1.xsd
    ├── .gitignore
    ├── enthic.dbdiagram.io
    ├── input
    ├── LICENSE.md
    ├── output
    │   ├── bundle.csv
    │   └── identity.csv
    ├── python
    │   ├── doc
    │   │   ├── conf.py
    │   │   ├── index.rst
    │   │   └── papit.png
    │   ├── enthic
    │   │   ├── app.py
    │   │   ├── company
    │   │   │   ├── company.py
    │   │   │   ├── denomination_company.py
    │   │   │   ├── __init__.py
    │   │   │   └── siren_company.py
    │   │   ├── database
    │   │   │   ├── mysql.py
    │   │   │   ├── mysql_data.py
    │   │   │   ├── fetchall.py
    │   │   │   └── __init__.py
    │   │   ├── configuration.json
    │   │   ├── conftest.py
    │   │   ├── decorator
    │   │   │   ├── check_sql_injection.py
    │   │   │   ├── __init__.py
    │   │   │   └── insert_request.py
    │   │   ├── extract_bundle.py
    │   │   ├── __init__.py
    │   │   ├── ontology.py
    │   │   ├── static
    │   │   │   ├── 404.html
    │   │   │   ├── 500.html
    │   │   │   ├── bootstrap.min.css
    │   │   │   ├── documentation
    │   │   │   │   ├── .buildinfo
    │   │   │   │   ├── doctrees
    │   │   │   │   │   ├── environment.pickle
    │   │   │   │   │   └── index.doctree
    │   │   │   │   ├── genindex.html
    │   │   │   │   ├── index.html
    │   │   │   │   ├── _modules
    │   │   │   │   │   ├── company
    │   │   │   │   │   │   ├── company.html
    │   │   │   │   │   │   ├── denomination_company.html
    │   │   │   │   │   │   └── siren_company.html
    │   │   │   │   │   ├── decorator
    │   │   │   │   │   │   ├── check_sql_injection.html
    │   │   │   │   │   │   └── insert_request.html
    │   │   │   │   │   ├── index.html
    │   │   │   │   │   └── utils
    │   │   │   │   │       ├── error_json_response.html
    │   │   │   │   │       ├── json_response.html
    │   │   │   │   │       ├── not_found_response.html
    │   │   │   │   │       └── ok_json_response.html
    │   │   │   │   ├── .nojekyll
    │   │   │   │   ├── objects.inv
    │   │   │   │   ├── py-modindex.html
    │   │   │   │   ├── search.html
    │   │   │   │   ├── searchindex.js
    │   │   │   │   ├── _sources
    │   │   │   │   │   └── index.rst.txt
    │   │   │   │   └── _static
    │   │   │   │       ├── ajax-loader.gif
    │   │   │   │       ├── alabaster.css
    │   │   │   │       ├── basic.css
    │   │   │   │       ├── comment-bright.png
    │   │   │   │       ├── comment-close.png
    │   │   │   │       ├── comment.png
    │   │   │   │       ├── custom.css
    │   │   │   │       ├── doctools.js
    │   │   │   │       ├── documentation_options.js
    │   │   │   │       ├── down.png
    │   │   │   │       ├── down-pressed.png
    │   │   │   │       ├── file.png
    │   │   │   │       ├── jquery-3.2.1.js
    │   │   │   │       ├── jquery.js
    │   │   │   │       ├── language_data.js
    │   │   │   │       ├── minus.png
    │   │   │   │       ├── papit.png
    │   │   │   │       ├── plus.png
    │   │   │   │       ├── pygments.css
    │   │   │   │       ├── searchtools.js
    │   │   │   │       ├── underscore-1.3.1.js
    │   │   │   │       ├── underscore.js
    │   │   │   │       ├── up.png
    │   │   │   │       ├── up-pressed.png
    │   │   │   │       └── websupport.js
    │   │   │   ├── favicon.ico
    │   │   │   ├── google7775f38904c3d3fc.html
    │   │   │   ├── index.html
    │   │   │   ├── jquery.min.js
    │   │   │   ├── robot.txt
    │   │   │   ├── sitemap.xml
    │   │   │   ├── swagger.json
    │   │   │   ├── swagger-ui-bundle.js
    │   │   │   ├── swagger-ui-bundle.js.map
    │   │   │   ├── swagger-ui.css
    │   │   │   ├── swagger-ui.css.map
    │   │   │   ├── swagger-ui.js
    │   │   │   ├── swagger-ui.js.map
    │   │   │   ├── swagger-ui-standalone-preset.js
    │   │   │   └── swagger-ui-standalone-preset.js.map
    │   │   ├── test_app.py
    │   │   ├── test_extract_bundle.py
    │   │   ├── test_treat_bundle.py
    │   │   ├── treat_bundle.py
    │   │   └── utils
    │   │       ├── error_json_response.py
    │   │       ├── conversion.py
    │   │       ├── __init__.py
    │   │       ├── json_response.py
    │   │       ├── not_found_response.py
    │   │       └── ok_json_response.py
    │   ├── __init__.py
    │   ├── MANIFEST.in
    │   ├── setup.cfg
    │   └── setup.py
    ├── README.rst
    ├── sh
    │   ├── check-data.sh
    │   ├── database-creation.sh
    │   ├── database-update.sh
    │   ├── install-dependencies.sh
    │   └── install-wheel.sh
    ├── sonar-project.properties
    └── sql
        ├── create-database-enthic.sql
        ├── create-index-bundle.sql
        ├── create-index-identity.sql
        ├── create-table-bundle.sql
        ├── create-table-identity.sql
        ├── create-table-request.sql
        ├── insert-bundle.sql
        └── insert-identity.sql

Donation
--------

You can donate to support Python and Open Source development.

**BTC** ``32JSkGXcBK2dirP6U4vCx9YHHjV5iSYb1G``

**ETH** ``0xF556505d13aC9a820116d43c29dc61417d3aB2F8``
