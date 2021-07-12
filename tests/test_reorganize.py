# test_reorganize.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from zettelkasten_tools.reorganize import corrections_elements
from .context import zettelkasten_tools as zt
import re


def test_attach_missing_ids():
    test_list = [
        '5_10_Senescent_cells_9e051e2c4.md',
        '1_2_reframe_your_goal_as_a_learning_goal.md',
        '2_1a_render_md_files_with_python_and_flask_41e5a496c.md',
        '2_5_homebrew.md']
    command_list = zt.reorganize.attach_missing_ids(test_list)
    assert len(command_list) == 2
    assert command_list[0][0] == 'rename'
    assert zt.handle_filenames.get_filename_components(
        command_list[0][2])[0] == '1_2'
    assert zt.handle_filenames.get_filename_components(
        command_list[0][2])[1] == 'reframe_your_goal_as_a_learning_goal'
    assert re.match(r'.*_[0-9a-f]{9}\.md$', command_list[0][2])


def test_generate_tokenized_list():
    test_list = [
        '5_10_Senescent_cells_9e051e2c4.md',
        '1_2_reframe_your_goal_as_a_learning_goal_ab9df245b.md',
        '2_1a_render_md_files_with_python_and_flask_ab9df245b.md',
        '2_5_homebrew_282f521b1.md']
    tokenized_list = zt.reorganize.generate_tokenized_list(test_list)
    assert tokenized_list[0][0][0] == '5'
    assert tokenized_list[1][0][1] == '2'
    assert tokenized_list[0][1] == '5_10_Senescent_cells_9e051e2c4.md'


def test_corrections_elements():
    list_of_keys = ['1', '2', '4', '5', '5a', '6', '7', '8', '8a', '8b', '9']
    corrections_elements = zt.reorganize.corrections_elements(list_of_keys)
    assert corrections_elements['1'] == '01'
    assert corrections_elements['8b'] == '10'


def test_corrections_elements_shrink():
    # subtrees have been removed
    list_of_keys = ['01', '02', '10', '11']
    corrections_elements = zt.reorganize.corrections_elements(list_of_keys)
    assert corrections_elements['01'] == '1'
    assert corrections_elements['11'] == '4'


def test_generate_tree():
    test_list = [
        '1_first_topic_41b4e4f8f.md',
        '1_1_a_Thought_on_first_topic_2c3c34ff5.md',
        '1_2_another_Thought_on_first_topic_2af216153.md',
        '2_Second_Topic_cc6290ab7.md',
        '2_1_a_Thought_on_Second_Topic_176fb43ae.md']
    tokenized_list = zt.reorganize.generate_tokenized_list(test_list)
    assert tokenized_list == [
        [['1'], '1_first_topic_41b4e4f8f.md'],
        [['1', '1'], '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
        [['1', '2'], '1_2_another_Thought_on_first_topic_2af216153.md'],
        [['2'], '2_Second_Topic_cc6290ab7.md'],
        [['2', '1'], '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]
    tree = zt.reorganize.generate_tree(tokenized_list)
    assert tree == [
        ['1', '1_first_topic_41b4e4f8f.md',
            [
                ['1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
                ['2', '1_2_another_Thought_on_first_topic_2af216153.md']]],
        ['2', '2_Second_Topic_cc6290ab7.md',
            [['1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]]]


def test_reorganize_filenames():
    tree = [
        ['1', '1_first_topic_41b4e4f8f.md',
            [
                ['1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
                ['2', '1_2_another_Thought_on_first_topic_2af216153.md']]],
        ['2', '2_Second_Topic_cc6290ab7.md',
            [['1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]]]
    changes = zt.reorganize.reorganize_filenames(tree)
    assert changes == [
        ['1', '1_first_topic_41b4e4f8f.md'],
        ['1_1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
        ['1_2', '1_2_another_Thought_on_first_topic_2af216153.md'],
        ['2', '2_Second_Topic_cc6290ab7.md'],
        ['2_1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]


def test_create_rename_commands():
    potential_changes = [
        ['1', '1_first_topic_41b4e4f8f.md'],
        ['1_1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
        ['1_2', '1_5_another_Thought_on_first_topic_2af216153.md'],
        ['2', '2_Second_Topic_cc6290ab7.md'],
        ['2_1', '2_3_a_Thought_on_Second_Topic_176fb43ae.md']]
    command_list = zt.reorganize.create_rename_commands(potential_changes)
    assert command_list == [
        ['rename',
            '1_5_another_Thought_on_first_topic_2af216153.md',
            '1_2_another_Thought_on_first_topic_2af216153.md'],
        ['rename',
            '2_3_a_Thought_on_Second_Topic_176fb43ae.md',
            '2_1_a_Thought_on_Second_Topic_176fb43ae.md', ]]
