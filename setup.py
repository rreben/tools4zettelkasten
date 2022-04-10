# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license


from setuptools import setup

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tools4zettelkasten',
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
            'tools4zettelkasten = tools4zettelkasten:ZettelkastenTools.run'
        ],
    },
)
