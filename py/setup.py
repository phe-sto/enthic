# -*- coding: utf-8 -*-

from distutils.core import setup

NAME = 'enthic'
setup(name=NAME,
      version='0.1',
      description='Extract INPI result account data',
      author='Christophe Brun',
      author_email='christophe.brun@papit.fr',
      url='https://www.papit.fr/',
      packages=[NAME, NAME + ".utils"],
      )
