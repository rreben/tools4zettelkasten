# test_reorganize.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import zettelkasten_tools as zt
import re


def test_generate_tokenized_list():
    test_list = [
        '5_10_Senescent_cells.md',
        '1_2_reframe_your_goal_as_a_learning_goal.md',
        '2_1a_render_md_files_with_python_and_flask.md',
        '2_5_homebrew.md']
    tokenized_list = zt.reorganize.generate_tokenized_list(test_list)
    assert tokenized_list[0][0][0] == '5'
    assert tokenized_list[1][0][1] == '2'
    assert tokenized_list[0][1] == '5_10_Senescent_cells.md'
