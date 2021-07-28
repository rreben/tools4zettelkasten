# stage.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from tools4zettelkasten.settings import ZETTELKASTEN_INPUT
import logging
from tools4zettelkasten.persistency import (
    rename_file,
    file_content,
    is_markdown_file,
    is_text_file,
    list_of_filenames_from_directory
)
from tools4zettelkasten.handle_filenames import create_base_filename_from_title
import os


def process_txt_file(directory, filename):
    newfilename = 'Error'
    content = file_content(directory, filename)
    if len(content) == 0:
        logging.warning(
            "File ", filename,
            "in directory", directory,
            "can not be processed, no valid markdown header")
    elif (content[0][0] == '#'):
        newfilename = create_base_filename_from_title(
            content[0][2:])
        rename_file(directory, filename, newfilename + ".md")


def process_files_from_input(directory):
    list_of_filenames = list_of_filenames_from_directory(directory)
    for filename in list_of_filenames:
        if (
            is_text_file(filename)
            or
            is_markdown_file(filename)
        ):
            print(process_txt_file(directory, filename))
