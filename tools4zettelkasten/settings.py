# settings.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

import os
import logging

from dotenv import load_dotenv

load_dotenv(override=False)

logger = logging.getLogger(__name__)

ZETTELKASTEN = os.environ.get('ZETTELKASTEN', '../zettelkasten/mycelium')
ZETTELKASTEN_INPUT = os.environ.get('ZETTELKASTEN_INPUT',
                                    '../zettelkasten/input')

# Flask settings
TEMPLATE_FOLDER = 'flask_frontend/templates'
STATIC_FOLDER = 'flask_frontend/static'
ZETTELKASTEN_IMAGES = os.environ.get(
    'ZETTELKASTEN_IMAGES',
    '/Users/rupertrebentisch/Dropbox/zettelkasten/mycelium/images')

# Description of structural links in Zettelkasten
DIRECT_SISTER_ZETTEL = "train of thoughts"
DIRECT_DAUGHTER_ZETTEL = "detail / digression"

# RAG settings
CHROMA_DB_PATH = os.environ.get(
    'CHROMA_DB_PATH',
    os.path.expanduser('~/.tools4zettelkasten/chroma_db'))
EMBEDDING_MODEL = os.environ.get(
    'EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o')


def check_directories(strict: bool = True):
    """Validate that configured directories exist.

    :param strict: If True, exit on missing directory (CLI mode).
                   If False, log warnings only (MCP server mode).
    """
    for name, path in [
        ('ZETTELKASTEN', globals()['ZETTELKASTEN']),
        ('ZETTELKASTEN_INPUT', globals()['ZETTELKASTEN_INPUT']),
        ('ZETTELKASTEN_IMAGES', globals()['ZETTELKASTEN_IMAGES']),
    ]:
        if not os.path.isdir(path):
            msg = (
                f"{path} is not a directory, "
                f"please set {name} to a valid directory."
            )
            if strict:
                from colorama import Fore, Style
                print(Style.BRIGHT + Fore.RED + msg)
                exit(1)
            else:
                logger.warning(msg)
