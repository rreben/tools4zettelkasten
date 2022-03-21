# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

# See https://click.palletsprojects.com/en/8.0.x/
#     setuptools/#setuptools-integration
# on how to use setuptools with the Click package.

from setuptools import setup

import tools4zettelkasten

setup(
    name='tools4zettelkasten',
    version=tools4zettelkasten.__version__,
    description=(
        'This project provides tools to setup' +
        'a Zettelkasten System based on simple interlinked markdown files'),
    author='Dr. Rupert Rebentisch',
    author_email='rupert.rebentisch@gmail.com',
    url='https://github.com/rreben/tools4zettelkasten',
    py_modules=['tools4zettelkasten'],
    install_requires=[
        'Click',
        'colorama',
        'Flask',
        'Flask-PageDown',
        'Flask-WTF',
        'graphviz',
        'importlib-metadata',
        'inquirerpy',
        'itsdangerous',
        'Jinja2',
        'Markdown',
        'MarkupSafe',
        'pfzy',
        'prompt-toolkit',
        'pyfiglet',
        'Pygments',
        'wcwidth',
        'Werkzeug',
        'WTForms',
        'zipp'
    ],
    entry_points={
        'console_scripts': [
            'tools4zettelkasten = tools4zettelkasten.cli:messages',
        ],
    },
)
