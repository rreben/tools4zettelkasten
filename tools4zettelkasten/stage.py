# stage.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import logging
from tools4zettelkasten.persistency import PersistencyManager
from tools4zettelkasten.handle_filenames import create_base_filename_from_title
from . import handle_filenames as hf


def process_txt_file(persistencyManager: PersistencyManager, filename):
    newbasefilename = 'Error'
    content = persistencyManager.get_file_content(filename)
    if len(content) == 0:
        logging.warning(
            "File ", filename,
            "in directory", persistencyManager.directory,
            "can not be processed, no valid markdown header")
    elif (content[0][0] == '#'):
        newbasefilename = create_base_filename_from_title(
            content[0][2:])
        ordering = ''
        id = ''
        if hf.is_valid_filename(filename):
            note = hf.create_Note(filename)
            ordering = note.ordering
            id = note.id
        if hf.create_filename(ordering, newbasefilename, id) != filename:
            persistencyManager.rename_file(
                filename, hf.create_filename(ordering, newbasefilename, id))


def process_files_from_input(persistencyManager: PersistencyManager):
    list_of_filenames = persistencyManager.get_list_of_filenames()
    for filename in list_of_filenames:
        if (
            persistencyManager.is_text_file(filename)
            or
            persistencyManager.is_markdown_file(filename)
        ):
            process_txt_file(persistencyManager, filename)
