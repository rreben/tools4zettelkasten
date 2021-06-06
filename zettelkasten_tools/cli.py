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


@click.group()
def messages():
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
def stage():
    click.echo('stage input')


@click.command(help='add ids, consecutive numbering, keep links life')
def reorganize():
    click.echo('reorganize')


messages.add_command(stage)
messages.add_command(reorganize)
