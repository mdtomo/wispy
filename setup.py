#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='wispy',
    version='0.0.1',
    license='MIT',
    long_description=open('README.md').read(),
    packages=['wispy', 'python_radiotap', 'pcapy'],
)
