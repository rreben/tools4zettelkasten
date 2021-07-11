# reorganize.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from . import handle_filenames as hf
import re


def attach_missing_ids(file_name_list):
    """Generates a list of commands to attach missing ids by renaming files

    :param file_name_list: List of files in a given directory which might
        contain filenames with missing ids.
    :type file_name_list: list of strings
    :return: list of commands. Each command is a list with three components.
        the command (i.e. rename), the old filename and the new filename.
    :rtype: list of list of strings
    """
    command_list = []
    for filename in file_name_list:
        components = hf.get_filename_components(filename)
        if components[2] == '':
            oldfilename = filename
            file_id = hf.generate_id(filename)
            newfilename = components[0] + '_' + components[1][:-3] + \
                '_' + file_id + '.md'
            command_list.append(['rename', oldfilename, newfilename])
    return command_list


def generate_tokenized_list(zettelkasten_list):
    tokenized_list = []
    for filename in zettelkasten_list:
        filename_components = hf.get_filename_components(filename)
        numbering_in_filename_and_filename = [
            re.split(r'_', filename_components[0]), filename]
        # if match:
        #    trunk_filen_name = match.group()
        tokenized_list.append(numbering_in_filename_and_filename)
    return tokenized_list
