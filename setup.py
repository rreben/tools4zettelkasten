# setup.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license


from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tools4zettelkasten',
    packages=find_packages(),
    description=(
        'This project provides tools to setup' +
        'a Zettelkasten System based on simple interlinked markdown files'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Dr. Rupert Rebentisch',
    author_email='rupert.rebentisch@gmail.com',
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
    extras_require={
        'mcp': ['mcp[cli]>=1.0.0'],
    },
    include_package_data=True,
    package_data={'': ['tools4zettelkasten/VERSION']},
    entry_points={
        'console_scripts': [
            'tools4zettelkasten = tools4zettelkasten:ZettelkastenTools.run'
        ],
    },
)
