# handle_filenames.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

import re
import hashlib
from datetime import datetime


def create_base_filename_from_title(title):
    """Create a standard base filename

    Suppose you have a title like 5 Dinge für mein Thema.
    This will give
    Dinge_fuer_mein_Thema
    This string is suited as a standard base filename for
    the Zettelkasten.

    Parameters:
    title (str): The title of the note

    Returns:
    filename_base (str): string for base_filename
    """
    # filename extension is md
    # remove leading and trailing whitespaces
    filename_base = title.strip()
    # remove multiple whitespaces
    filename_base = " ".join(filename_base.split())
    # replace all öäüß with oe, ae, ue, ss
    filename_base = filename_base.replace("ä", "ae")
    filename_base = filename_base.replace("ö", "oe")
    filename_base = filename_base.replace("ü", "ue")
    filename_base = filename_base.replace("Ä", "Ae")
    filename_base = filename_base.replace("Ö", "Oe")
    filename_base = filename_base.replace("Ü", "Ue")
    filename_base = filename_base.replace("ß", "ss")
    # replace all spaces with underscore
    filename_base = filename_base.replace(" ", "_")
    # remove special characters like ?
    filename_base = re.sub('[^A-Za-z0-9_]+', '', filename_base)
    return filename_base


def get_filename_components(filename):
    """Decomposes a standard note filename

    A standard filename has the form of
    2_03_04a_5_Some_Topic_fb134b00b
    Where 2_03_04a_5 define the order within
    the hierachy of notes (in this case 4 levels),
    Some_Topic is the base of the filename
    and fb134b00b is a unique identifier.
    The return value is
    ['2_03_04a_5','Some_Topic','fb134b00b']

    Parameters:
    filename (str): The filename of a note

    Returns:
    components (list): List of strings with the components of the filename
    """
    components = []
    id_filename = ''
    if re.match(r'.*_[0-9a-f]{9}\.md$', filename):
        id_filename = filename[-12:-3]
        filename = filename[:-13]
    # Split by first underscore followed by a character = Non-Digit
    ordering_filename = re.split(r'_\D', filename, maxsplit=1)[0]
    base_filename = filename[(len(ordering_filename)+1):]
    components = [ordering_filename, base_filename, id_filename]
    return components


def generate_id(filename):
    """generates an unique Id for a file

    IDs have the form of 8 hex digits.
    Like fb134b00b. As collisions are unlikely
    but not impossible the seed is peppered with
    a timestamp.

    Parameters:
    filename (str): The filename of a note

    Returns:
    (str): id in form of 8 hex digits
    """
    return evaluate_sha_256(filename + currentTimestamp())[:9]


def evaluate_sha_256(input):
    input = input.encode('utf-8')
    hash_object = hashlib.sha256(input)
    hex_dig = hash_object.hexdigest()
    return(hex_dig)


def currentTimestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S%f")
