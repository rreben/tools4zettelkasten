# stage.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from zettelkasten_tools.settings import ZETTELKASTEN_INPUT
from zettelkasten_tools.persistency import list_of_filenames_from_directory
import os


def process_txt_file(pathname):
    filename = 'Error'
    with open(pathname, 'r') as afile:
        content = afile.readlines()
        if (content[0][0] == '#'):
            filename = content[0][2:]
            filename = handle_filenames.create_base_filename_from_title(
                filename)
        os.rename(pathname, input_directory + '/' + filename + '.md')


def process_files_from_input():
    list_of_filenames = list_of_filenames_from_directory(ZETTELKASTEN_INPUT)
    for filename in list_of_filenames:
        if (
            'txt' ==
            os.path.splitext(filename)[1][1:].strip().lower()
            or
            'md' ==
            os.path.splitext(filename)[1][1:].strip().lower()
        ):
            print(process_txt_file(ZETTELKASTEN_INPUT + '/' + filename))
