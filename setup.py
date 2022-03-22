# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license


from setuptools import setup

import re
import io
import importlib.util

"""See https://click.palletsprojects.com/en/8.0.x/
setuptools/#setuptools-integration
on how to use setuptools with the Click package.

We need to read the version from the package's __init__.py file.
But we can't import the package, because it has to be installed first.
The import statement for the package will work only if all dependencies
are installed already. When we do a clean build, the import will break.
Therefore we read the version from the package's __init__.py file with
a regex. This is a bit hacky, but works. The other option would be to
set the version number in the setup.py file and read it from there.
But this involves a lot some runtime magic and the version is in the wrong
place.
See https://stackoverflow.com/
questions/17583443/what-is-the-correct-way-to-share-package-version-
with-setup-py-and-the-package
for a discussion on this topic."""


version_from_module = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('tools4zettelkasten/__init__.py', encoding='utf_8_sig').read()
).group(1)

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tools4zettelkasten',
    version=version_from_module,
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
            'tools4zettelkasten = tools4zettelkasten.cli:messages'
        ],
    },
)
