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


def check_path_exists(path_to_check: str) -> bool:
    """Check if a path exists (file or directory).

    :param path_to_check: Path to check
    :type path_to_check: str
    :return: True if path exists, False otherwise
    :rtype: bool
    """
    return path.isdir(path_to_check) or path.isfile(path_to_check)


def get_env_var_status(var_name: str) -> tuple:
    """Get environment variable status.

    :param var_name: Name of the environment variable
    :type var_name: str
    :return: Tuple of (is_set, value or None)
    :rtype: tuple
    """
    try:
        value = env[var_name]
        return (True, value)
    except KeyError:
        return (False, None)


def format_settings_output():
    """Format and display current settings in a structured box."""
    # Collect all data for width calculation
    paths_data = [
        ("Zettelkasten:", st.ZETTELKASTEN),
        ("Input:", st.ZETTELKASTEN_INPUT),
        ("Images:", st.ZETTELKASTEN_IMAGES),
    ]
    flask_data = [
        ("Templates:", st.TEMPLATE_FOLDER),
        ("Static files:", st.STATIC_FOLDER),
    ]
    hierarchy_data = [
        ("Sister Zettel:", st.DIRECT_SISTER_ZETTEL),
        ("Daughter Zettel:", st.DIRECT_DAUGHTER_ZETTEL),
    ]
    rag_data = [
        ("ChromaDB path:", st.CHROMA_DB_PATH),
        ("Embedding model:", st.EMBEDDING_MODEL),
        ("Top K results:", str(st.RAG_TOP_K)),
        ("LLM model:", st.LLM_MODEL),
    ]
    env_vars = [
        "ZETTELKASTEN", "ZETTELKASTEN_INPUT", "ZETTELKASTEN_IMAGES",
        "CHROMA_DB_PATH", "EMBEDDING_MODEL", "RAG_TOP_K", "LLM_MODEL",
    ]

    # Calculate box width
    header = f"tools4zettelkasten v{__version__}"
    max_label_len = 20
    max_value_len = max(
        max(len(str(v)) for _, v in paths_data),
        max(len(str(v)) for _, v in flask_data),
        max(len(str(v)) for _, v in hierarchy_data),
        max(len(str(v)) for _, v in rag_data),
        max(len(v) for v in env_vars) + 25,  # for status text
    )
    box_width = max(len(header) + 4, max_label_len + max_value_len + 10)

    def print_box_line(content: str, color=Fore.WHITE):
        """Print a line within the box."""
        print(Fore.CYAN + "║" + color + content.ljust(box_width) +
              Fore.CYAN + "║")

    def print_section_header(title: str):
        """Print a section header."""
        print(Fore.CYAN + "╠" + "═" * box_width + "╣")
        print_box_line(f"  {title}", Style.BRIGHT + Fore.WHITE)

    def print_path_line(label: str, value: str):
        """Print a path line with validation status."""
        exists = check_path_exists(value)
        status = Fore.GREEN + "✓" if exists else Fore.RED + "✗"
        line = f"    {label:<18} {value}"
        # Truncate if too long
        max_val_width = box_width - 26
        if len(value) > max_val_width:
            display_val = "..." + value[-(max_val_width - 3):]
        else:
            display_val = value
        line = f"    {label:<18} {display_val}"
        padding = box_width - len(line) - 3
        print(Fore.CYAN + "║" + Fore.WHITE + line +
              " " * padding + status + " " + Fore.CYAN + "║")

    def print_value_line(label: str, value: str):
        """Print a simple label-value line."""
        line = f"    {label:<18} {value}"
        print_box_line(line)

    def print_env_var_line(var_name: str):
        """Print environment variable status line."""
        is_set, _ = get_env_var_status(var_name)
        if is_set:
            status = Fore.GREEN + "✓ set"
            line = f"    {var_name:<24} {status}"
        else:
            status = Fore.YELLOW + "✗ not set (using default)"
            line = f"    {var_name:<24} "
        print(Fore.CYAN + "║" + Fore.WHITE + f"    {var_name:<24} " +
              (Fore.GREEN + "✓ set" if is_set else
               Fore.YELLOW + "✗ not set (using default)") +
              " " * (box_width - 30 - len(var_name) -
                     (5 if is_set else 25)) + Fore.CYAN + "║")

    def print_secret_var_line(var_name: str):
        """Print secret environment variable status (never show value)."""
        is_set, _ = get_env_var_status(var_name)
        print(Fore.CYAN + "║" + Fore.WHITE + f"    {var_name:<24} " +
              (Fore.GREEN + "✓ set" if is_set else
               Fore.RED + "✗ not set") +
              " " * (box_width - 30 - len(var_name) -
                     (5 if is_set else 9)) + Fore.CYAN + "║")

    # Print header
    print(Fore.CYAN + "╔" + "═" * box_width + "╗")
    print(Fore.CYAN + "║" + Style.BRIGHT + Fore.CYAN +
          header.center(box_width) + Style.RESET_ALL + Fore.CYAN + "║")

    # Working Directories section
    print_section_header("WORKING DIRECTORIES")
    for label, value in paths_data:
        print_path_line(label, value)

    # Flask Configuration section
    print_section_header("FLASK CONFIGURATION")
    for label, value in flask_data:
        print_path_line(label, value)

    # Hierarchy Links section
    print_section_header("HIERARCHY LINKS")
    for label, value in hierarchy_data:
        print_value_line(label, value)

    # RAG Configuration section
    print_section_header("RAG CONFIGURATION")
    for label, value in rag_data:
        print_value_line(label, value)

    # Environment Variables section
    print_section_header("ENVIRONMENT VARIABLES")
    for var_name in env_vars:
        print_env_var_line(var_name)
    print_secret_var_line("OPENAI_API_KEY")

    # Print footer
    print(Fore.CYAN + "╚" + "═" * box_width + "╝")
    print(Style.RESET_ALL)


def show_banner():
    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))
    print("Copyright (c) 2021 Rupert Rebentisch, Version: ", __version__)




@click.group()
def messages():
    show_banner()
    init(autoreset=True)
    print('Initializing of tools4zettelkasten ...')
    st.check_directories(strict=True)
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


@click.command(help='show version and current settings')
def settings():
    """Display version and current configuration settings."""
    format_settings_output()


@click.command(help='start MCP server for Claude integration')
def mcp():
    try:
        from . import mcp_server
        mcp_server.run_server()
    except ImportError:
        print(Fore.RED + "MCP dependencies not installed.")
        print("Install with: pip install 'tools4zettelkasten[mcp]'")


@click.command(help='sync zettelkasten into vector database')
@click.option('--full', is_flag=True, default=False,
              help='rebuild vector database from scratch')
@click.option('--stats', is_flag=True, default=False,
              help='show vector database statistics only')
def vectorize(full, stats):
    try:
        from . import rag
    except ImportError:
        print(Fore.RED + "RAG dependencies not installed.")
        print("Install with: pip install 'tools4zettelkasten[rag]'")
        return

    if stats:
        try:
            store = rag.VectorStore()
            s = store.get_stats()
            print(f"Total documents: {s['total_documents']}")
            print(f"ChromaDB path:   {s['chroma_path']}")
            print(f"Embedding model: {s['embedding_model']}")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
        return

    persistencyManager = PersistencyManager(st.ZETTELKASTEN)

    if full:
        import chromadb
        import os
        print("Rebuilding vector database from scratch...")
        client = chromadb.PersistentClient(path=st.CHROMA_DB_PATH)
        try:
            client.delete_collection('zettelkasten')
        except ValueError:
            pass

    print("Syncing vector database...")
    store = rag.VectorStore()
    result = store.sync(persistencyManager)
    print(f"  Added:     {result.added} zettel")
    print(f"  Updated:   {result.updated} zettel")
    print(f"  Deleted:   {result.deleted} zettel")
    print(f"  Unchanged: {result.unchanged} zettel")
    print(f"  Metadata:  {result.metadata_updated} zettel updated "
          "(ordering/filename changes)")
    total = store.get_stats()['total_documents']
    print(f"Done. {total} zettel in vector database.")


@click.command(help='chat with your zettelkasten (RAG)')
@click.option('--top-k', default=None, type=int,
              help='number of zettel to retrieve per question')
def chat(top_k):
    try:
        from . import rag
    except ImportError:
        print(Fore.RED + "RAG dependencies not installed.")
        print("Install with: pip install 'tools4zettelkasten[rag]'")
        return

    import os
    if not os.environ.get('OPENAI_API_KEY'):
        print(Fore.RED + "OPENAI_API_KEY environment variable is not set.")
        print("Please set it to your OpenAI API key.")
        return

    store = rag.VectorStore()
    if store.get_stats()['total_documents'] == 0:
        print(Fore.YELLOW + "Vector database is empty. "
              "Run 'vectorize' first.")
        return

    print("Zettelkasten Chat (type 'quit' to exit)\n")
    conversation_history = []

    while True:
        try:
            query = input(Fore.CYAN + "You: " + Style.RESET_ALL)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.strip().lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if not query.strip():
            continue

        search_results = store.search(query, top_k=top_k)
        try:
            response = rag.chat_completion(
                query, search_results, conversation_history)
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
            continue

        print(f"\n{Fore.GREEN}Zettelkasten:{Style.RESET_ALL} {response}\n")

        print(Fore.YELLOW + "Quellen:" + Style.RESET_ALL)
        for r in search_results:
            print(f"  [{r.ordering}] {r.title} ({r.zettel_id})")
        print()

        conversation_history.append({'role': 'user', 'content': query})
        conversation_history.append({'role': 'assistant', 'content': response})


messages.add_command(stage)
messages.add_command(reorganize)
messages.add_command(analyse)
messages.add_command(start)
messages.add_command(settings)
messages.add_command(mcp)
messages.add_command(vectorize)
messages.add_command(chat)
messages.no_args_is_help
