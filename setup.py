# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

# See https://click.palletsprojects.com/en/8.0.x/
#     setuptools/#setuptools-integration
# on how to use setuptools with the Click package.

from setuptools import setup
# import sys
# import os

import re
import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('tools4zettelkasten/__init__.py', encoding='utf_8_sig').read()
).group(1)


setup(
    version=__version__,
    # ... etc.
)
# sys.path.insert(0, os.path.abspath(
#     os.path.join(os.path.dirname(__file__), '.')))

# import tools4zettelkasten  # noqa # pylint: disable=unused-import, wrong-import-position
with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tools4zettelkasten',
    version=__version__,
    description=(
        'This project provides tools to setup' +
        'a Zettelkasten System based on simple interlinked markdown files'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
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
