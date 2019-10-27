# PapIT French society accountability extraction and treatment

Low code project than treat data from opendata-rncs.inpi.fr. They contain xml
files of the account declaration of all french societies. The overall project
is meant to be a low-code one.

## Install dependencies
Interpreter and VM for python are embedded is the project code. Only synaptic
packages have to be installed.

```sh ./install-dependencies.sh```

## Extact data from zip

Data are stored in zip files on opendata-rncs.inpi.fr, group by month. Each xml is zip. The first step is then to extract the xml files.

```sh ./clear-data.sh```

## Check the xml format

An XSD is provided by the INPI. This step verify all the xml are following this
XSD. XML not following this XSD have their filename printed out.

```sh ./check-data.sh```