# settings.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

import os
import logging

logger = logging.getLogger(__name__)

ZETTELKASTEN = '../zettelkasten/mycelium'
ZETTELKASTEN_INPUT = '../zettelkasten/input'

# Flask settings
TEMPLATE_FOLDER = 'flask_frontend/templates'
STATIC_FOLDER = 'flask_frontend/static'
ZETTELKASTEN_IMAGES = (
    '/Users/rupertrebentisch/Dropbox/zettelkasten/mycelium/images')

# Description of structural links in Zettelkasten
DIRECT_SISTER_ZETTEL = "train of thoughts"
DIRECT_DAUGHTER_ZETTEL = "detail / digression"


def overwrite_setting(environment_variable: str):
    """Overwrite a module-level setting with the value of an environment variable.

    If the environment variable is not set, a log message is emitted.

    :param environment_variable: name of the environment variable
    """
    value = os.environ.get(environment_variable)
    if value:
        globals()[environment_variable] = value
    else:
        logger.info(
            f"{environment_variable} not set in environment, "
            "tools4zettelkasten will default to built-in setting. "
            "Use the 'settings' command to find out more."
        )


def overwrite_settings():
    """Apply environment variable overrides to all configurable settings."""
    overwrite_setting('ZETTELKASTEN')
    overwrite_setting('ZETTELKASTEN_INPUT')
    overwrite_setting('ZETTELKASTEN_IMAGES')


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
