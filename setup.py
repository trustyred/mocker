#!/usr/bin/env python

from distutils.core import setup
import mocker

setup(
    name='Mocker',
    version=mocker.__version__,
    description='Python example implementation of the Docker engine',
    author='Anthony Shaw',
    author_email='gward@python.net',
    url='https://www.python.org/sigs/distutils-sig/',
    # py_modules = ['mocker'],
    packages=['mocker'],
    scripts=['scripts/mocker']
    requires=['requests','docopt','']
    )
