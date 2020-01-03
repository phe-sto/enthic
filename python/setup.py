# -*- coding: utf-8 -*-

from os.path import join

import enthic
from setuptools import setup, find_packages
from sphinx.application import Sphinx

################################################################################
# BUILD THE DOCUMENTATION WITH SPHINX FRAMEWORK
builder = "html"
srcdir = "source"
builddir = join("./enthic/static/documentation")
doctreedir = join(builddir, "doctrees")

# Create the Sphinx application object
app = Sphinx(srcdir, srcdir, builddir, doctreedir, builder)

# Run the build
app.build()

################################################################################
# BUILD OR INSTALL THE PACKAGE
NAME = 'enthic'
setup(name=NAME,
      version=enthic.__version__,
      description='Extract INPI result account data',
      author=enthic.__author__,
      author_email=enthic.__email__,
      url='https://www.papit.fr/',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': ['sum-bundle = enthic.treat_bundle:main'],
          'console_scripts': ['extract-bundle = enthic.extract_bundle:main'],
          'console_scripts': ['enthic-api = enthic.app:main'],
      },
      install_requires=[
          'flask', 'flask-mysqldb', 'requests', 'pytest', 'sphinx', 'flask-cors'
      ]
      )
