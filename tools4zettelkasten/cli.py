# cli.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license
"""The command line interface.

Click is used as backbone for the cli.
An excellent tutorial is found at "https://zetcode.com/python/click".
"""

import click
from pyfiglet import Figlet
from . import settings
# we have to rename stage so it does not interfere with command stage
from . import stage as stg
from .persistency import PersistencyManager
from . import reorganize as ro
from . import analyse as an
from . import flask_views as fv
from . import __version__
from InquirerPy import prompt
from dataclasses import dataclass


@dataclass()
class Command:
    pass


@dataclass()
class Replace_command(Command):
    filename: str
    to_be_replaced: str
    replace_with: str


def batch_replace(
        command_list: list[Replace_command],
        persistencyManager: PersistencyManager):
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": False,
        }
    ]
    print(command_list)
    result = prompt(questions)
    if result["proceed"]:
        for command in command_list:
            file_content = persistencyManager.get_string_from_file_content(
                command.filename)
            new_file_content = file_content.replace(
                command.to_be_replaced,
                command.replace_with)
            persistencyManager.overwrite_file_content(
                command.filename, new_file_content)


def batch_rename(command_list, persistencyManager: PersistencyManager):
    """rename a bunch of file

    prompt user to verify that rename should be done

    :param command_list: A list of rename commands.
    Each command is a list with three entries.
    name of command, must be rename.
    oldfilename original name of file.
    newfilename name of file after rename operation.

    :type command_list: list
    :param persistencyManager: handler for manipulation of the file system
    :type persistencyManager: PersistencyManager
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
                persistencyManager.rename_file(
                    oldfilename, newfilename)


def show_banner():
    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))
    print("Copyright (c) 2021 Rupert Rebentisch, Version: ", __version__)


@click.group()
def messages():
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
@click.option(
    '--fully/--no-fully',
    default=False,
    help='Add perliminary ordering and ID',
    show_default=True
)
def stage(fully):
    show_banner()
    persistencyManager = PersistencyManager(
        settings.ZETTELKASTEN_INPUT)
    stg.process_files_from_input(persistencyManager)
    if fully:
        print('Searching for missing IDs')
        batch_rename(
            ro.attach_missing_ids(
                persistencyManager.get_list_of_filenames()),
            persistencyManager)
        print('Searching for missing orderingss')
        batch_rename(
            ro.attach_missing_orderings(
                persistencyManager.get_list_of_filenames()),
            persistencyManager)


@click.command(help='add ids, consecutive numbering, keep links alife')
def reorganize():
    show_banner()
    persistencyManager = PersistencyManager(
        settings.ZETTELKASTEN)
    print('Searching for missing IDs')
    batch_rename(
        ro.attach_missing_ids(
            persistencyManager.get_list_of_filenames()), persistencyManager)
    print('Searching for necessary changes in hierachy')
    tokenized_list = ro.generate_tokenized_list(
        persistencyManager.get_list_of_filenames())
    tree = ro.generate_tree(tokenized_list)
    potential_changes = ro.reorganize_filenames(tree)
    batch_rename(ro.create_rename_commands(
        potential_changes), persistencyManager)
    print('Searching for invalid links')
    list_of_commands = ro.generate_list_of_link_correction_commands(
        persistencyManager)
    batch_replace(list_of_commands, persistencyManager)


@click.command(help='analyse your Zettelkasten')
@click.option(
        '-t',
        '--type',
        help='type of analysis',
        type=click.Choice(['graph', 'tree'], case_sensitive=False),
        default='graph',
        show_default=True
    )
def analyse(type):
    show_banner()
    print(type)
    print("Analysing the Zettelkasten")
    persistencyManager = PersistencyManager(
        settings.ZETTELKASTEN)
    analysis = an.create_graph_analysis(
        persistencyManager)
    print("Number of Zettel: ", len(analysis.list_of_filenames))
    if (type == 'tree'):
        an.show_tree_as_list(analysis.tree)
    else:
        dot = an.create_graph_of_zettelkasten(
            analysis.list_of_filenames,
            analysis.list_of_links,
            url_in_nodes=False)
        an.show_graph_of_zettelkasten(dot)


@click.command(help='start flask server')
def start():
    show_banner()
    print("starting flask server")
    fv.run_flask_server()


messages.add_command(stage)
messages.add_command(reorganize)
messages.add_command(analyse)
messages.add_command(start)
messages.no_args_is_help
