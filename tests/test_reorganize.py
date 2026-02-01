# test_reorganize.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import tools4zettelkasten as zt
import re


def test_get_list_of_invalid_links(tmp_path):
    """Test finding all invalid links in directory of notes
    ToDo:
    * Write Test
    """
    content = """# A file containing links

    some text. some more text.

    [a link](1_07_a_target_176fb43ae.md)

    some
    different text [an inline link](1_1_a_Thought_on_first_topic_2c3c34ff5.md)

    ![image link](some_image.jpg)

    [a third link](1_1_a_Thought_on_first_topic_2c3c34ff5.md) and [a fourth link](2_3_a_Thought_on_Second_Topic_176fb43ae.md) test # noqa
    more to come"""
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.PersistencyManager(test_sub_dir)
    first_testfile = test_sub_dir / "1_05_a_file_containinglinks_2af216153.md"
    first_testfile.write_text(content)
    second_testfile = test_sub_dir / "1_07_a_target_176fb43ae.md"
    second_testfile.write_text("target 1")
    third_testfile = test_sub_dir / "1_1_a_Thought_on_first_topic_2c3c34ff5.md"
    third_testfile.write_text("target 2")
    fourth_testfile = (
        test_sub_dir / "2_04_a_Thought_on_Second_Topic_176fb43ae.md")
    fourth_testfile.write_text("changed target 3")

    assert first_testfile.read_text() == content
    assert second_testfile.read_text() == "target 1"
    assert third_testfile.read_text() == "target 2"
    assert len(zt.get_list_of_invalid_links(persistency_manager)) == 1
    linklist = zt.get_list_of_invalid_links(persistency_manager)
    assert linklist[0].source == "1_05_a_file_containinglinks_2af216153.md"
    assert linklist[0].description == "a fourth link"
    assert linklist[0].target == "2_3_a_Thought_on_Second_Topic_176fb43ae.md"


def test_attach_missing_orderings():
    test_list = [
        '5_10_Senescent_cells_9e051e2c4.md',
        'some_cloud_idea.md',
        '1_2_reframe_your_goal_as_a_learning_goal.md',
        '2_1a_render_md_files_with_python_and_flask_41e5a496c.md',
        'some_other_cloud_idea_43e5a488c.md',
        '2_5_homebrew.md']
    command_list = zt.attach_missing_orderings(test_list)
    assert len(command_list) == 2
    assert isinstance(command_list[0], zt.cli.Rename_command)
    assert zt.handle_filenames.get_filename_components(
        command_list[0].new_filename)[0] == '0_0'
    assert zt.handle_filenames.get_filename_components(
        command_list[0].new_filename)[1] == 'some_cloud_idea'


def test_attach_missing_ids():
    test_list = [
        '5_10_Senescent_cells_9e051e2c4.md',
        '1_2_reframe_your_goal_as_a_learning_goal.md',
        '2_1a_render_md_files_with_python_and_flask_41e5a496c.md',
        '2_5_homebrew.md',
        'no_ordering.md']
    command_list = zt.attach_missing_ids(test_list)
    assert len(command_list) == 3
    assert isinstance(command_list[0], zt.cli.Rename_command)
    assert zt.handle_filenames.get_filename_components(
        command_list[0].new_filename)[0] == '1_2'
    assert zt.handle_filenames.get_filename_components(
        command_list[0].new_filename)[1] == 'reframe_your_goal_as_a_learning_goal'
    assert re.match(r'.*_[0-9a-f]{9}\.md$', command_list[0].new_filename)
    assert isinstance(command_list[2], zt.cli.Rename_command)
    assert zt.handle_filenames.get_filename_components(
        command_list[2].new_filename)[0] == ''
    assert zt.handle_filenames.get_filename_components(
        command_list[2].new_filename)[1] == 'no_ordering'
    assert re.match(r'.*_[0-9a-f]{9}\.md$', command_list[2].new_filename)


def test_generate_tokenized_list():
    test_list = [
        '5_10_Senescent_cells_9e051e2c4.md',
        '1_2_reframe_your_goal_as_a_learning_goal_ab9df245b.md',
        '2_1a_render_md_files_with_python_and_flask_ab9df245b.md',
        '2_5_homebrew_282f521b1.md']
    tokenized_list = zt.generate_tokenized_list(test_list)
    assert tokenized_list[0][0][0] == '5'
    assert tokenized_list[1][0][1] == '2'
    assert tokenized_list[0][1] == '5_10_Senescent_cells_9e051e2c4.md'


def test_corrections_elements():
    list_of_keys = ['1', '2', '4', '5', '5a', '6', '7', '8', '8a', '8b', '9']
    corrections_elements = zt.corrections_elements(list_of_keys)
    assert corrections_elements['1'] == '01'
    assert corrections_elements['8b'] == '10'


def test_corrections_elements_shrink():
    # subtrees have been removed
    list_of_keys = ['01', '02', '10', '11']
    corrections_elements = zt.corrections_elements(list_of_keys)
    assert corrections_elements['01'] == '1'
    assert corrections_elements['11'] == '4'


def test_generate_tree():
    test_list = [
        '1_first_topic_41b4e4f8f.md',
        '1_1_a_Thought_on_first_topic_2c3c34ff5.md',
        '1_2_another_Thought_on_first_topic_2af216153.md',
        '2_Second_Topic_cc6290ab7.md',
        '2_1_a_Thought_on_Second_Topic_176fb43ae.md']
    tokenized_list = zt.generate_tokenized_list(test_list)
    assert tokenized_list == [
        [['1'], '1_first_topic_41b4e4f8f.md'],
        [['1', '1'], '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
        [['1', '2'], '1_2_another_Thought_on_first_topic_2af216153.md'],
        [['2'], '2_Second_Topic_cc6290ab7.md'],
        [['2', '1'], '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]
    tree = zt.generate_tree(tokenized_list)
    assert tree == [
        ['1', '1_first_topic_41b4e4f8f.md',
            [
                ['1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
                ['2', '1_2_another_Thought_on_first_topic_2af216153.md']]],
        ['2', '2_Second_Topic_cc6290ab7.md',
            [['1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]]]


def test_get_hierarchy_links():
    test_filenames = [
        '1_One_000000001.md',
        '1_1_One_One_000000002.md',
        '1_1_1_One_One_One_000000006.md',
        '1_1_2_One_One_Two_000000007.md',
        '1_2_One_Two_000000003.md',
        '1_3_One_Three_000000004.md',
        '2_Two_000000005.md'
    ]
    tokenized_list = zt.generate_tokenized_list(test_filenames)
    # print(tokenized_list)
    assert tokenized_list == [
        [['1'], '1_One_000000001.md'],
        [['1', '1'], '1_1_One_One_000000002.md'],
        [['1', '1', '1'], '1_1_1_One_One_One_000000006.md'],
        [['1', '1', '2'], '1_1_2_One_One_Two_000000007.md'],
        [['1', '2'], '1_2_One_Two_000000003.md'],
        [['1', '3'], '1_3_One_Three_000000004.md'],
        [['2'], '2_Two_000000005.md']]
    tree = zt.generate_tree(tokenized_list)
    # print(tree)
    assert tree == [
        ['1', '1_One_000000001.md',
            [['1', '1_1_One_One_000000002.md',
                [
                    ['1', '1_1_1_One_One_One_000000006.md'],
                    ['2', '1_1_2_One_One_Two_000000007.md']]],
                ['2', '1_2_One_Two_000000003.md'],
                ['3', '1_3_One_Three_000000004.md']]],
        ['2', '2_Two_000000005.md']]
    hierarchy_links = zt.get_hierarchy_links(tree)
    print(hierarchy_links)
    assert len(hierarchy_links) == 5
    assert hierarchy_links == [
        zt.Link(
            source='1_1_One_One_000000002.md',
            description='train of thoughts',
            target='1_2_One_Two_000000003.md'),
        zt.Link(
            source='1_2_One_Two_000000003.md',
            description='train of thoughts',
            target='1_3_One_Three_000000004.md'),
        zt.Link(
            source='1_One_000000001.md',
            description='detail / digression',
            target='1_1_One_One_000000002.md'),
        zt.Link(
            source='1_1_1_One_One_One_000000006.md',
            description='train of thoughts',
            target='1_1_2_One_One_Two_000000007.md'),
        zt.Link(
            source='1_1_One_One_000000002.md',
            description='detail / digression',
            target='1_1_1_One_One_One_000000006.md')]


def test_reorganize_filenames():
    tree = [
        ['1', '1_first_topic_41b4e4f8f.md',
            [
                ['1', '1_1_a_Thought_on_first_topic_2c3c34ff5.md'],
                ['2', '1_2_another_Thought_on_first_topic_2af216153.md']]],
        ['2', '2_Second_Topic_cc6290ab7.md',
            [['1', '2_1_a_Thought_on_Second_Topic_176fb43ae.md']]]]
    changes = zt.reorganize_filenames(tree)
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
    command_list = zt.create_rename_commands(potential_changes)
    assert len(command_list) == 2
    assert isinstance(command_list[0], zt.cli.Rename_command)
    assert command_list[0].old_filename == \
        '1_5_another_Thought_on_first_topic_2af216153.md'
    assert command_list[0].new_filename == \
        '1_2_another_Thought_on_first_topic_2af216153.md'
    assert isinstance(command_list[1], zt.cli.Rename_command)
    assert command_list[1].old_filename == \
        '2_3_a_Thought_on_Second_Topic_176fb43ae.md'
    assert command_list[1].new_filename == \
        '2_1_a_Thought_on_Second_Topic_176fb43ae.md'


def test_get_list_of_links_from_file(tmpdir):
    p = tmpdir.mkdir("subdir").join(
        "1_05_a_file_containinglinks_2af216153.md")
    content = """# A file containing links

    some text. some more text.

    [a link](1_07_a_target_176fb43ae.md)

    some
    different text [an inline link](1_1_a_Thought_on_first_topic_2c3c34ff5.md)

    ![image link](some_image.jpg)

    [a third link](1_1_a_Thought_on_first_topic_2c3c34ff5.md) and [a fourth link](2_3_a_Thought_on_Second_Topic_176fb43ae.md) test # noqa
    more to come"""
    p.write(content)
    assert p.read() == content
    assert len(tmpdir.listdir()) == 1
    links = zt.get_list_of_links_from_file(
        "1_05_a_file_containinglinks_2af216153.md", p.readlines())
    assert len(links) == 4
    assert links[0].source == "1_05_a_file_containinglinks_2af216153.md"
    assert links[0].description == 'a link'
    assert links[0].target == '1_07_a_target_176fb43ae.md'
    assert links[1].source == "1_05_a_file_containinglinks_2af216153.md"
    assert links[1].description == 'an inline link'
    assert links[1].target == '1_1_a_Thought_on_first_topic_2c3c34ff5.md'
    assert links[2].source == "1_05_a_file_containinglinks_2af216153.md"
    assert links[2].description == 'a third link'
    assert links[2].target == '1_1_a_Thought_on_first_topic_2c3c34ff5.md'
    assert links[3].source == "1_05_a_file_containinglinks_2af216153.md"
    assert links[3].description == 'a fourth link'
    assert links[3].target == '2_3_a_Thought_on_Second_Topic_176fb43ae.md'


def test_generate_tokenized_list_with_alpha_in_middle():
    """Test tokenization with alphanumeric orderings in middle positions"""
    test_list = [
        '14_35_08_Test_Existing_000000001.md',
        '14_35_08a_Test_New_Main_000000002.md',
        '14_35_08a_1_Test_Sub_One_000000003.md',
        '14_35_08a_2_Test_Sub_Two_000000004.md',
        '14_35_09_Test_Another_000000005.md'
    ]
    tokenized_list = zt.generate_tokenized_list(test_list)
    # Verify tokenization splits correctly at underscores
    assert tokenized_list[0][0] == ['14', '35', '08']
    assert tokenized_list[1][0] == ['14', '35', '08a']
    assert tokenized_list[2][0] == ['14', '35', '08a', '1']
    assert tokenized_list[3][0] == ['14', '35', '08a', '2']
    assert tokenized_list[4][0] == ['14', '35', '09']


def test_reorganize_with_alpha_in_middle():
    """Test full reorganization with alphanumeric orderings in middle positions"""
    test_list = [
        '14_35_08_Test_Existing_000000001.md',
        '14_35_08a_Test_New_Main_000000002.md',
        '14_35_08a_1_Test_Sub_One_000000003.md',
        '14_35_08a_2_Test_Sub_Two_000000004.md',
        '14_35_09_Test_Another_000000005.md'
    ]
    tokenized_list = zt.generate_tokenized_list(test_list)
    tree = zt.generate_tree(tokenized_list)
    changes = zt.reorganize_filenames(tree)
    rename_commands = zt.create_rename_commands(changes)

    # Verify tree structure is correctly built
    assert len(tree) > 0

    # Verify reorganization produces canonical orderings
    # After reorganization:
    # 14_35_08 stays as 1_1_1 (relative position)
    # 14_35_08a becomes 1_1_2
    # 14_35_08a_1 becomes 1_1_2_1
    # 14_35_08a_2 becomes 1_1_2_2
    # 14_35_09 becomes 1_1_3

    # Check that changes are generated
    assert len(changes) == 5

    # The new orderings should be canonical (no alpha suffixes)
    for change in changes:
        new_ordering = change[0]
        # Canonical orderings should only contain digits and underscores
        assert re.match(r'^[0-9_]+$', new_ordering), \
            f"Ordering '{new_ordering}' should be canonical (no letters)"


def test_corrections_elements_with_alpha_keys():
    """Test that corrections_elements handles alphanumeric keys correctly"""
    # Simulates keys from a subtree with alpha suffixes
    list_of_keys = ['08', '08a', '08a', '09']
    # Remove duplicates as generate_tree does
    list_of_keys = list(dict.fromkeys(list_of_keys))
    corrections = zt.corrections_elements(list_of_keys)

    # 08 -> 1, 08a -> 2, 09 -> 3
    assert corrections['08'] == '1'
    assert corrections['08a'] == '2'
    assert corrections['09'] == '3'
