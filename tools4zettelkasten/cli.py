# cli.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

"""The command line interface.

Click is used as backbone for the cli.
An excellent tutorial is found at "https://zetcode.com/python/click".
"""

import click
from pyfiglet import Figlet
# we have to rename stage so it does not interfere with command stage
from . import stage as stg
from .persistency import PersistencyManager
from . import reorganize as ro
from . import analyse as an
from . import flask_views as fv
from . import settings as st
from . import __version__
from InquirerPy import prompt
from dataclasses import dataclass
from os import environ as env
from os import path
from colorama import init, Fore, Style


@dataclass()
class Command:
    pass


@dataclass()
class Replace_command(Command):
    filename: str
    to_be_replaced: str
    replace_with: str


@dataclass()
class Rename_command(Command):
    old_filename: str
    new_filename: str


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


def format_rename_output(command_list: list[Rename_command]):
    """Format and display planned rename operations.

    :param command_list: List of Rename_command objects
    :type command_list: list[Rename_command]
    """
    if not command_list:
        print(Fore.YELLOW + "Keine Umbenennungen erforderlich.")
        return

    count = len(command_list)
    header = f"Geplante Umbenennungen ({count})"

    # Calculate box width based on longest filename
    max_len = max(
        max(len(cmd.old_filename), len(cmd.new_filename))
        for cmd in command_list
    )
    box_width = max(len(header) + 4, max_len + 10)

    # Print header
    print(Fore.CYAN + "╔" + "═" * box_width + "╗")
    print(Fore.CYAN + "║" + header.center(box_width) + "║")
    print(Fore.CYAN + "╠" + "═" * box_width + "╣")

    # Print each rename operation
    for i, cmd in enumerate(command_list, 1):
        line1 = f"  {i}. {cmd.old_filename}"
        line2 = f"     → {cmd.new_filename}"
        print(Fore.CYAN + "║" + Fore.WHITE + line1.ljust(box_width) +
              Fore.CYAN + "║")
        print(Fore.CYAN + "║" + Fore.GREEN + line2.ljust(box_width) +
              Fore.CYAN + "║")

    # Print footer
    print(Fore.CYAN + "╚" + "═" * box_width + "╝")
    print(Style.RESET_ALL)


def batch_rename(
        command_list: list[Rename_command],
        persistencyManager: PersistencyManager):
    """Rename a batch of files with single confirmation.

    Displays all planned renames, asks for confirmation once,
    then executes all renames in order.

    :param command_list: A list of Rename_command objects.
    :type command_list: list[Rename_command]
    :param persistencyManager: handler for manipulation of the file system
    :type persistencyManager: PersistencyManager
    """
    if not command_list:
        format_rename_output(command_list)
        return

    format_rename_output(command_list)

    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": False
        }
    ]

    result = prompt(questions)
    if result["proceed"]:
        for command in command_list:
            persistencyManager.rename_file(
                command.old_filename, command.new_filename)


def show_banner():
    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))
    print("Copyright (c) 2021 Rupert Rebentisch, Version: ", __version__)


def overwrite_setting(environment_variable: str):
    """overwrite the variables in the settings modules
    with environment variables.

    If not set, the a warning is printed.

    There is an exec clause. When the value of the environment variable is
    set to ZETTELKASTEN and the environment is set
    to /somepath, the exec clause will be evaluated to
    exec (st.Zettelkasten = "/somepath")

    :param environment_variable: name of the environment variable"""
    try:
        if env[environment_variable]:
            exec(
                "%s = %s" % (
                    "st." + environment_variable,
                    '"' + env[environment_variable] + '"'))
    except KeyError:
        print(
            Style.BRIGHT + Fore.BLUE +
            f"{environment_variable} not set in environment, " +
            "tools4zettelkasten will default to built-in setting. " +
            "Use the 'show' command to find out more."
        )


def overwrite_settings():
    overwrite_setting('ZETTELKASTEN')
    overwrite_setting('ZETTELKASTEN_INPUT')
    overwrite_setting('ZETTELKASTEN_IMAGES')


def check_directories():
    if not path.isdir(st.ZETTELKASTEN):
        print(
            Style.BRIGHT + Fore.RED +
            f"{st.ZETTELKASTEN} is not a directory, " +
            "please set ZETTELKASTEN to a valid directory."
        )
        exit(1)
    if not path.isdir(st.ZETTELKASTEN_INPUT):
        print(
            Style.BRIGHT + Fore.RED +
            f"{st.ZETTELKASTEN_INPUT} is not a directory, " +
            "please set ZETTELKASTEN_INPUT to a valid directory."
        )
        exit(1)
    if not path.isdir(st.ZETTELKASTEN_IMAGES):
        print(
            Style.BRIGHT + Fore.RED +
            f"{st.ZETTELKASTEN_IMAGES} is not a directory, " +
            "please set ZETTELKASTEN_IMAGES to a valid directory."
        )
        exit(1)


@click.group()
def messages():
    show_banner()
    init(autoreset=True)
    print('Initializing of tools4zettelkasten ...')
    overwrite_settings()
    check_directories()
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
@click.option(
    '--fully/--no-fully',
    default=True,
    help='Add perliminary ordering and ID',
    show_default=True
)
def stage(fully):
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN_INPUT)
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
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
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
    print(type)
    print("Analysing the Zettelkasten")
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
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
    print("starting flask server")
    fv.run_flask_server()


@click.command(help='show version and settings')
def show():
    print()
    print('Here is the configuration')
    print('Working directories')
    print(
        'Path to the Zettelkasten: ',
        st.ZETTELKASTEN,
        ' can be set via ZETTELKASTEN environment variable')
    print(
        'Path to the Zettelkasten input: ',
        st.ZETTELKASTEN_INPUT,
        ' can be set via ZETTELKASTEN_INPUT environment variable')
    print()
    print('Flask configuration')
    print('Path to templates: ', st.TEMPLATE_FOLDER)
    print('Path to static files: ', st.STATIC_FOLDER)
    print(
        'Path to images for flask: ',
        st.ZETTELKASTEN_IMAGES,
        ' can be set via ZETTELKASTEN_IMAGES environment variable')
    print()
    print('What we write to automatically generated hierachy links')
    print('comment for sister Zettel: ', st.DIRECT_SISTER_ZETTEL)
    print('comment for daughter Zettel: ', st.DIRECT_DAUGHTER_ZETTEL)
    print('Built-in settings can be changed in the settings.py file')


messages.add_command(stage)
messages.add_command(reorganize)
messages.add_command(analyse)
messages.add_command(start)
messages.add_command(show)
messages.no_args_is_help
