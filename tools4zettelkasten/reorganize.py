# reorganize.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import logging
from . import handle_filenames as hf
from . import cli as cli
from .persistency import PersistencyManager
from dataclasses import dataclass
import re


@dataclass()
class Link:
    '''Object for representing a link between notes'''
    source: str
    description: str
    target: str


def generate_list_of_link_correction_commands(
        persistencyManager: PersistencyManager):
    command_list = []
    list_of_invalid_links = get_list_of_invalid_links(persistencyManager)
    files_dict = generate_dictionary(
        persistencyManager.get_list_of_filenames())
    for invalid_link in list_of_invalid_links:
        target = invalid_link.target
        target_id = hf.get_filename_components(target)[2]
        valid_target = ''
        if target_id in files_dict:
            valid_target = files_dict[target_id]
        else:
            print(
                "no file with id: " +
                str(target_id) +
                " found for link in file: " +
                invalid_link.source +
                "Pls correct manually")
        command = cli.Replace_command(
            filename=invalid_link.source,
            to_be_replaced=(
                "[" + invalid_link.description + "]"
                + "(" + target + ")"),
            replace_with=(
                "[" + invalid_link.description + "]"
                + "(" + valid_target + ")"
            )
        )
        command_list.append(command)
    return command_list


def get_list_of_invalid_links(persistency_manager: PersistencyManager):
    invalid_links = []
    for file in persistency_manager.get_list_of_filenames():
        lines_of_filecontent = (
            persistency_manager.get_file_content(filename=file))
        if len(lines_of_filecontent) > 0:
            list_of_links_in_file = (
                get_list_of_links_from_file(
                    file,
                    lines_of_filecontent=lines_of_filecontent))
        else:
            logging.error("empty file: " + file)
        for link in list_of_links_in_file:
            if not persistency_manager.is_file_existing(link.target):
                invalid_links.append(link)
    return invalid_links


def get_list_of_links_from_file(filename, lines_of_filecontent):
    """find all links in a file

    Only links to other files are returned. Links for images are ignored.

    :param lines_of_filecontent: the content of the file as list of strings
    :type lines_of_filecontent: list of strings
    :return: list of Link dataclass objects
    :rtype: list of Link objects
    """
    list_of_links = []
    # there might be multiple links in one line
    # there might be links to images
    link_reg_ex = re.compile(
        r'!{0,1}\[[a-zA-Z0-9_ !]*\]\([a-zA-Z0-9_]*\.md\)')
    link_reg_ex_with_groups = re.compile(
        r'\[([a-zA-Z0-9_ !]*)\]\(([a-zA-Z0-9_]*\.md)\)')
    for line in lines_of_filecontent:
        # first we gather all links from a given line
        # we do not use groups here, because
        # it is easier to process groups within each found link
        links_found_strings = link_reg_ex.findall(line)
        for link_found in links_found_strings:
            # If the line contains one ore more links
            # each link is tested if it is a link to an image
            # which schould be ignored
            if (
                isinstance(link_found, str)
                and
                link_found[0] != '!'
            ):
                # We then match the description and the target and
                # form the result to a Link object
                link_match = link_reg_ex_with_groups.search(link_found)
                if link_match:
                    list_of_links.append(
                        Link(
                            filename,
                            link_match.group(1),
                            link_match.group(2)))
    return list_of_links


def attach_missing_ids(file_name_list):
    """Generates a list of commands to attach missing ids by renaming files

    Suppose we have the following list as input:

    ['5_10_Senescent_cells_9e051e2c4.md',
    '1_2_reframe_your_goal_as_a_learning_goal.md',
    '2_1a_render_md_files_with_python_and_flask_41e5a496c.md',
    '2_5_homebrew.md']

    Then the following command_list will be retrurned:

    [['rename', '1_2_reframe_your_goal_as_a_learning_goal.md',
    '1_2_reframe_your_goal_as_a_learning_goal_7ae870951.md'],
    ['rename', '2_5_homebrew.md', '2_5_homebrew_fe38ebbaa.md']]

    Remark: The Ids are seeded with the timestamp. So the Ids will
    change with every new run of the program or test.

    :param file_name_list: List of files in a given directory which might
        contain filenames with missing ids.
    :type file_name_list: list of strings
    :return: list of commands. Each command is a list with three components.
        the command (i.e. rename), the old filename and the new filename.
    :rtype: list of list of strings

    ToDo:
    *   Implement mechanism to resolve hash collisions
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


def generate_dictionary(zettelkasten_list: list[str]) -> dict[str, str]:
    """generates a list from a list of Zettelkasten filenames

    :param zettelkasten_list: List of filenames in the Zettelkasten
    :type zettelkasten_list: list[str]
    :return: dictionary with the id as keys and the filename as values
    :rtype: dictionary
    """
    zettelkasten_dict = {}
    for filename in zettelkasten_list:
        zettelkasten_dict[
            hf.get_filename_components(filename=filename)[2]] = filename
    return zettelkasten_dict


def generate_tokenized_list(zettelkasten_list):
    """generates a list of tokens from a file list

    Suppose the list of filenames for input is:

    ['5_10_Senescent_cells_9e051e2c4.md',
    '1_2_reframe_your_goal_as_a_learning_goal_ab9df245b.md',
    '2_1a_render_md_files_with_python_and_flask.md_41e5a496c',
    '2_5_homebrew.md_282f521b1']

    Then the function will return:

    [[['5', '10'], '5_10_Senescent_cells_9e051e2c4.md'],
    [['1', '2'], '1_2_reframe_your_goal_as_a_learning_goal_ab9df245b.md'],
    [['2', '1a'], '2_1a_render_md_files_with_python_and_flask.md_41e5a496c'],
    [['2', '5'], '2_5_homebrew.md_282f521b1']]

    :param zettelkasten_list: the list of filennames
    :type zettelkasten_list: list
    :return: a list of list of ordering items and filenames
    :rtype: list
    """
    tokenized_list = []
    for filename in zettelkasten_list:
        filename_components = hf.get_filename_components(filename)
        numbering_in_filename_and_filename = [
            re.split(r'_', filename_components[0]), filename]
        # if match:
        #    trunk_filen_name = match.group()
        tokenized_list.append(numbering_in_filename_and_filename)
    return tokenized_list


def corrections_elements(list_of_keys):
    """corrects numberings to canonical form

    Suppose you have named your files in one level
    and one subtree like as follows.

    ['1', '2', '4', '5', '5a', '6', '7', '8', '8a', '8b', '9']

    Then you get a dictionary which you can use
    to bring the numbers to a canonical form:

    {'1': '01',
    '2': '02',
    '4': '03',
    '5': '04',
    '5a': '05',
    '6': '06',
    '7': '07',
    '8': '08',
    '8a': '09',
    '8b': '10',
    '9': '11'}

    :param list_of_keys: numbering keys of one subtree and one level
    :type list_of_keys: list
    :return: what key to set for which original key to get
             a canonical numbering
    :rtype: dictionary
    """
    list_of_keys_with_leading_zeros = []
    corrections_elements_dict = {}
    number_of_necessary_digits = len(str(abs(len(list_of_keys))))
    # sort keys in a way that
    # 8, 8a, 10, 11
    # is sorted like
    # 08, 08a, 10, 11
    # and not like
    # 10, 11, 8, 8a what a simple sort would do
    for i in range(len(list_of_keys)):
        number_of_digits = sum(c.isdigit() for c in list_of_keys[i])
        leading_zeros = '0' * (number_of_necessary_digits - number_of_digits)
        list_of_keys_with_leading_zeros.append(
            [list_of_keys[i], leading_zeros + list_of_keys[i]])
    list_of_keys_with_leading_zeros.sort(key=lambda x: x[1])
    # now form canonical numbering scheme and make the corrections
    # as elements of the dictionary
    for i in range(len(list_of_keys_with_leading_zeros)):
        j = i + 1
        number_of_digits = sum(c.isdigit() for c in str(j))
        leading_zeros = '0' * (number_of_necessary_digits - number_of_digits)
        list_of_keys_with_leading_zeros[i].append(leading_zeros + str(j))
        corrections_elements_dict[
            list_of_keys_with_leading_zeros[i][0]] = (
                list_of_keys_with_leading_zeros[i][2])
    return corrections_elements_dict


def generate_tree(tokenized_list):
    """generates a tree from a tokenized list

    Suppose we have the following files:

    ['1_first_topic_41b4e4f8f.md',
    '1_1_a_Thought_on_first_topic_2c3c34ff5.md',
    '1_2_another_Thought_on_first_topic_2af216153.md',
    '2_Second_Topic_cc6290ab7.md',
    '2_1_a_Thought_on_Second_Topic_176fb43ae.md']

    After tokenizing (which is done elsewhere)
    we get

    [[['1'], '1_first_topic_41b4e4f8f.md'],
    [['1', '1'], '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
    [['1', '2'], '1_2_another_Thought_on_first_topic_2af216153.md'],
    [['2'], '2_Second_Topic_cc6290ab7.md'],
    [['2', '1'], '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]

    This is our input. generate_tree will do a recursion
    to form a tree like:

    [['1', '1_first_topic_41b4e4f8f.md',
        [['1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
        ['2', '1_2_another_Thought_on_first_topic_2af216153.md']]],
    ['2', '2_Second_Topic_cc6290ab7.md',
        [['1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]]]

    :param tokenized_list: the tokenized list of hierchical files
    :type tokenized_list: list
    :return: structured tree
    :rtype: list
    """
    # prepare canonical correction of keys in each
    # level of recursion
    tree_keys = [x[0][0] for x in tokenized_list]
    tree_keys.sort()
    # remove duplicates
    tree_keys = list(dict.fromkeys(tree_keys))
    corrections_elements_dict = corrections_elements(tree_keys)
    tree = []
    for tree_key in tree_keys:
        sub_tree = []
        sub_tokenized_list = []
        sub_tree.append(corrections_elements_dict[tree_key])
        for x in tokenized_list:
            if x[0][0] == tree_key:
                if len(x[0]) == 1:
                    sub_tree.append(x[1])
                else:
                    sub_tokenized_list.append([x[0][1:], x[1]])
                    # sub_tree.append(generate_tree([x[0][1:],x[1]]))
        # sub_tree.append([[x[0][1:],
        # x[1]] for x in tokenized_list if x[0][0] == tree_key])
        if len(sub_tokenized_list) > 0:
            sub_tree.append(generate_tree(sub_tokenized_list))
        tree.append(sub_tree)
    tree.sort(key=lambda x: x[0])
    return tree


def reorganize_filenames(tree, path=None, final=None):
    if final is None:
        final = []
    if path is None:
        path = ''
    for node in tree:
        if isinstance(node, list):
            if len(node) == 2:
                if isinstance(node[0], str) and isinstance(node[1], str):
                    final.append(
                        [path + node[0], node[1]])
                else:
                    reorganize_filenames(node, path=path, final=final)
            else:
                if len(node) == 3:
                    if (
                        isinstance(node[0], str)
                        and isinstance(node[1], str)
                        and isinstance(node[2], list)
                    ):
                        final.append([path + node[0], node[1]])
                        reorganize_filenames(
                            node[2], path=path + node[0] + '_', final=final)
                else:
                    reorganize_filenames(node, path=path, final=final)
        else:
            path += node + '_'
    return final


def create_rename_commands(potential_changes_of_filenames):
    changes_of_filenames = [
        ['rename', x[1],
            x[0]
            + '_'
            + hf.get_filename_components(x[1])[1]
            + '_'
            + hf.get_filename_components(x[1])[2]
            + '.md']
        for x in potential_changes_of_filenames
        if x[0] != hf.get_filename_components(x[1])[0]]
    return changes_of_filenames
