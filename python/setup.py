# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

NAME = 'enthic'
setup(name=NAME,
      version='0.1',
      description='Extract INPI result account data',
      author='Christophe Brun',
      author_email='christophe.brun@papit.fr',
      url='https://www.papit.fr/',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': ['sum-bundle = enthic.sum_bundle:main'],
          'console_scripts': ['extract-bundle = enthic.extract_bundle:main'],
          'console_scripts': ['enthic-api = enthic.app:main'],
      },
      install_requires=[
          'flask', 'flask-mysqldb', 'requests'
      ]
      )
