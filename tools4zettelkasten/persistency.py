# persistency.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import os
import logging


def is_file_existing(directory, filename) -> bool:
    if os.path.exists(directory):
        if (os.path.isfile(os.path.join(directory, filename))
                and
                # do not process hidden files
                not (filename[0] == '.')):
            return True
        else:
            return False
    else:
        logging.error(
            "rename-error: directrory "
            + directory + " not found")


def rename_file(directory, oldfilename, newfilename):
    """renames a file in a directory

    :param directory: the name of the directory containing the file
                      to be renamed
    :type directory: string
    :param oldfilename: original name of the file
    :type oldfilename: string
    :param newfilename: new name of the file
    :type newfilename: string
    """
    if os.path.exists(directory):
        oldfile = directory / oldfilename
        newfile = directory / newfilename
        os.rename(oldfile, newfile)
        print('renamed: ', oldfile, ' with: ', newfile)
    else:
        logging.error(
            "rename-error: directrory "
            + directory + " not found")


def list_of_filenames_from_directory(directory):
    """returns a list of all files in a directory

    Hidden files are excluded from the list

    :param directory: name of the directory
    :type directory: string
    :return: list of the names of the files in the directory
    :rtype: list
    """
    list_of_filenames = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            # do not process subfolders
            if (os.path.isfile(os.path.join(directory, filename))
                and
                # do not process hidden files
                    not (filename[0] == '.')):
                list_of_filenames.append(filename)
    else:
        logging.error(
            "input directrory" + " not found")
    return list_of_filenames


def is_text_file(filename):
    if 'txt' == os.path.splitext(filename)[1][1:].strip().lower():
        return True
    else:
        return False


def is_markdown_file(filename):
    if 'md' == os.path.splitext(filename)[1][1:].strip().lower():
        return True
    else:
        return False


def file_content(directory, filename):
    content = []
    with open(directory / filename, 'r') as afile:
        content = afile.readlines()
    return content


class PersistencyManager:
    def __init__(self, directory) -> None:
        self.directory = directory

    def get_list_of_filenames(self):
        return list_of_filenames_from_directory(directory=self.directory)

    def get_file_content(self, filename):
        return file_content(directory=self.directory, filename=filename)

    def is_file_existing(self, filename):
        return is_file_existing(directory=self.directory, filename=filename)
