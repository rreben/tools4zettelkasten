# cli.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license
"""The command line interface.

click is used as backbone for the cli.
An excellent tutorial is found at https://zetcode.com/python/click/

Todo:
    * connect new cli to functionality
"""

import click
from pyfiglet import Figlet
from . import settings
# we have to rename stage so it does not interfere with command stage
from . import stage as stg


@click.group()
def messages():
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
def stage():
    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))
    stg.process_files_from_input(settings.ZETTELKASTEN_INPUT)


@click.command(help='add ids, consecutive numbering, keep links life')
def reorganize():
    click.echo('reorganize')


messages.add_command(stage)
messages.add_command(reorganize)
