#!/usr/bin/env python3

from setuptools import setup, find_packages

exec(open('eecisc/__init__.py').read())

setup(
    name='eecisc',
    version=__version__,
    description='Tools for accessing eecisc.eng.cam.ac.uk.',
    maintainer='Tim Tröndle',
    maintainer_email='tt397@cam.ac.uk',
    url='https://www.github.com/timtroendle/eecisc',
    license='MIT',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=['pysmb', 'geopandas'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering'
    ]
)
