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
from . import persistency as pers
from . import reorganize as ro
from InquirerPy import prompt


def batch_rename(command_list, directory):
    """rename a bunch of file

    prompt user to verify that rename should be done

    :param command_list: A list of rename commands.
    Each command is a list with three entries.
    name of command, must be rename.
    oldfilename original name of file.
    newfilename name of file after rename operation.

    :type command_list: list
    :param directory: directory with files which shoud be renamed
    :type directory: string
    """
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": False,
        }
    ]
    for command in command_list:
        if command[0] == 'rename':
            oldfilename = command[1]
            newfilename = command[2]
            print('Rename ', oldfilename, ' --> ')
            print(newfilename, '?')
            result = prompt(questions)
            if result["proceed"]:
                pers.rename_file(directory, oldfilename, newfilename)


def show_banner():
    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))


@click.group()
def messages():
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
def stage():
    show_banner()
    stg.process_files_from_input(settings.ZETTELKASTEN_INPUT)


@click.command(help='add ids, consecutive numbering, keep links alife')
def reorganize():
    show_banner()
    batch_rename(
        ro.attach_missing_ids(
            pers.list_of_filenames_from_directory(settings.ZETTELKASTEN)),
        settings.ZETTELKASTEN)


messages.add_command(stage)
messages.add_command(reorganize)
