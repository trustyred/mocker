#!/usr/bin/env python

from setuptools import setup, find_packages
import mocker

setup(
    name='Mocker',
    version=mocker.__version__,
    description='Python example implementation of the Docker engine',
    author='nored',
    packages=find_packages(),
    scripts=['scripts/mocker'],    
    )
