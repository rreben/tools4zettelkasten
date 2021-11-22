# handle_filenames.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

"""functions to handle filenames

standard filenames have the form of
2_03_04a_5_Some_Topic_fb134b00b

The correct form of the filenames is
important for listing, reorganizing the
Zettelkasten etc.
"""

import re
import hashlib
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Note:
    """A note

    Attributes:
        ordering (str): The ordering of the note
        base_filename (str): The base of the filename
        id (str): The id of the note
    """
    ordering: str
    base_filename: str
    id: str


def is_valid_filename(filename) -> bool:
    """checks if a filename is valid

    Args:
        filename (str): The filename of a note

    Returns:
        bool: True if the filename is valid
    """
    note = create_Note(filename)
    if (is_valid_ordering(note.ordering)
            and is_valid_basefilename(note.base_filename)
            and is_valid_id(note.id)):
        return True


def create_Note(filename) -> Note:
    """create a Note object from a filename

    Args:
        filename (str): The filename of a note

    Returns:
        Note: Note object
    """
    components = get_filename_components(filename)
    ordering = components[0]
    base_filename = components[1]
    id = components[2]
    note = Note(ordering, base_filename, id)
    return note


def is_valid_basefilename(base_filename):
    """checks if a base filename is valid

    Args:
        base_filename (str): The base of the filename

    Returns:
        bool: True if the base filename is valid
    """
    if re.match(r'^[A-Za-z_]+$', base_filename):
        return True
    else:
        return False


def is_valid_ordering(ordering):
    """checks if an ordering is valid

    Args:
        ordering (str): The ordering of a note

    Returns:
        bool: True if the ordering is valid
    """
    if re.match(r'^[0-9_]+$', ordering):
        return True
    else:
        return False


def is_valid_id(id):
    """checks if an id is valid

    Args:
        id (str): The id of a note

    Returns:
        bool: True if the id is valid
    """
    if re.match(r'^[0-9a-f]{9}$', id):
        return True
    else:
        return False


def create_filename(ordering, base_filename, id) -> str:
    """Creates a standard filename

    Args:
        ordering (str): The ordering of the note
        base_filename (str): The base of the filename
        id (str): The id of the note

    Returns:
        str: filename
    """
    if ordering == '':
        filename = base_filename
    else:
        filename = ordering + '_' + base_filename
    if id != '':
        filename = filename + '_' + id + '.md'
    else:
        filename = filename + '.md'
    return filename


def create_base_filename_from_title(title):
    """Create a standard base filename

    Suppose you have a title like 5 Dinge für mein Thema.
    This will give
    Dinge_fuer_mein_Thema
    This string is suited as a standard base filename for
    the Zettelkasten.

    Args:
        title (str): The title of the note

    Returns:
        str: base_filename
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

    Args:
        filename (str): The filename of a note

    Returns:
        list: List of strings with the components of the filename
    """
    components = []
    id_filename = ''
    if re.match(r'.*_[0-9a-f]{9}\.md$', filename):
        id_filename = filename[-12:-3]
        filename = filename[:-13]
    else:
        id_filename = ''
        filename = filename[:-3]
    # Split by first underscore followed by a character = Non-Digit
    if re.match(r'^\d', filename):
        ordering_filename = re.split(r'_\D', filename, maxsplit=1)[0]
        base_filename = filename[(len(ordering_filename)+1):]
    else:
        ordering_filename = ''
        base_filename = filename
    components = [ordering_filename, base_filename, id_filename]
    return components


def generate_id(filename):
    """generates an unique Id for a file

    IDs have the form of 8 hex digits.
    Like fb134b00b. As collisions are unlikely
    but not impossible the seed is peppered with
    a timestamp.

    Args:
        filename (string): The filename of a note

    Returns:
        str: id in form of 8 hex digits
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
