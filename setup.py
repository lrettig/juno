#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='juno',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    # NOT CURRENTLY APPLICABLE. VERSION BUMPS MANUAL FOR NOW
    version='0.1.0',
    description='Juno',
    author='Lane Rettig',
    author_email='lanerettig@gmail.com',
    url='https://github.com/lrettig/juno',
    include_package_data=True,
    py_modules=[],
    install_requires=[
        'pywebassembly==0.1.0',
    ],
    license='MIT',
    zip_safe=False,
    keywords='ethereum blockchain evm trinity',
    packages=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    # trinity
    # entry_points={
    #     'console_scripts': ['trinity=trinity:main'],
    # },
)
