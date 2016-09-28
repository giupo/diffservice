#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'tornado',
    'sqlalchemy',
    'pysd==0.1.0',
    'pandas==0.18.1',
    'redis'
]

test_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-bdd',
    'pytest-xdist',
    'pytest-watch',
    'tox',
    'detox'
]

setup(
    name='diffservice',
    version='0.1.3',
    description='Service for compare Data and build reports',
    long_description=readme + '\n\n' + history,
    author='Giuseppe Acito',
    author_email='giuseppe.acito@gmail.com',
    url='https://github.com/giupo/diffservice',
    packages=find_packages(exclude="tests/*"),
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='diffservice',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    cmdclass={'test': PyTest},
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'diffservice=diffservice.app:main'
        ]
    },
    dependency_links=[
        'https://github.com/giupo/pysd/tarball/master#egg=pysd-0.1.0'
    ]
)
