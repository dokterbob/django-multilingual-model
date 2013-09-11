#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages

try:
    README = open('README.rst').read()
except:
    README = None

#try:
#    REQUIREMENTS = open('requirements.txt').lines()
#except:
#    REQUIREMENTS = None

setup(
    name='django-multilingual-model',
    version='0.5.1',
    description='Django Simple Multilingual Support for Models.',
    long_description=README,
    #install_requires=REQUIREMENTS,
    author='Mathijs de Bruin',
    author_email='mathijs@mathijsfietst.nl',
    url='http://github.com/dokterbob/django-multilingual-model',
    packages = find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
        'argparse',  # apparently needed by django-setuptest on python 2.6
    ),
)
