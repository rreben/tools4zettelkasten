# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

from setuptools import setup

setup(
    name='tools4zettelkasten',
    version='0.1.0',
    py_modules=['tools4zettelkasten'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'tools4zettelkasten = tools4zettelkasten:cli',
        ],
    },
)
