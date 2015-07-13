#!/usr/bin/env python

from os.path import join
from setuptools import setup, find_packages

setup(name='ldapass',
      version='0.1',
      description='Web application for setting/changing LDAP user passwords.'
      author='Bartek Rutkowski',
      author_email='contact+ldapass@robakdesign.com',
      license='BSD3',
      url='https://github.com/bartekrutkowski/ldapass',
      packages=find_packages(),
      entry_points = {'console_scripts': ['ldapass = ldapass:main',]},
      install_requires=['Flask', 'WTForms', 'python-ldap'],
      )
