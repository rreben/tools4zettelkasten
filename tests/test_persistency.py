# test_persistency.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import tools4zettelkasten as zt


def test_persistency_manager(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.PersistencyManager(tmp_path / "subdir")
    first_testfile = test_sub_dir / "1_05_a_file_containinglinks_2af216153.md"
    first_testfile.write_text("source")
    second_testfile = test_sub_dir / "1_07_a_target_176fb43ae.md"
    second_testfile.write_text("target 1")
    third_testfile = test_sub_dir / "1_1_a_Thought_on_first_topic_2c3c34ff5.md"
    third_testfile.write_text("target 2")
    fourth_testfile = (
        test_sub_dir / "2_04_a_Thought_on_Second_Topic_176fb43ae.md")
    fourth_testfile.write_text("changed target 3")
    assert persistency_manager.is_file_existing("1_07_a_target_176fb43ae.md")


def test_create_file(tmpdir):
    """Creates a temporary test file and reads it back in

    The test uses the standard fixture in pytest to work
    with test files
    The fixture is described in
    https://docs.pytest.org/en/6.2.x/tmpdir.html

    :param tmpdir: this parameter is set as test fixture
                   by the pytest system
    :type tmpdir: directory
    ToDo:
    * Test PersistencyManager
    """
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    assert p.read() == "content"
    assert len(tmpdir.listdir()) == 1


def test_is_file_existing(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    testfile = test_sub_dir / "test.md"
    testfile.write_text("some info")
    assert zt.is_file_existing(test_sub_dir, "test.md")
    assert not zt.is_file_existing(test_sub_dir, "nonexiting.md")


def test_rename_file(tmp_path):
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    persistency_manager = zt.PersistencyManager(tmp_path / "subdir")
    testfile = test_dir / "test.md"
    testfile.write_text("some info")
    persistency_manager.rename_file("test.md", "new.md")
    comparefile = test_dir / "new.md"
    assert comparefile.exists()
    assert comparefile.read_text() == "some info"


def test_list_of_filenames_from_directory(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    first_testfile = test_sub_dir / "test.md"
    first_testfile.write_text("some info")
    second_testfile = test_sub_dir / "test_scnd.md"
    second_testfile.write_text("some other info")
    list_of_filenames = zt.list_of_filenames_from_directory(str(test_sub_dir))
    assert len(list_of_filenames) == 2
    assert list_of_filenames[1] == "test.md"
    assert list_of_filenames[0] == "test_scnd.md"


def test_is_text_file():
    assert zt.is_text_file("some.txt")
    assert zt.is_text_file("some.jpg") is False


def test_is_markdown_file():
    assert zt.is_markdown_file("some.md")
    assert zt.is_markdown_file("some.jpg") is False


def test_file_content(tmp_path):
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    testfile = test_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    testfile.write_text(content)
    content = zt.file_content(test_dir, "test.md")
    assert len(content) == 3
    assert content[0][0] == "#"


def test_get_string_from_file_content(tmp_path):
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    testfile = test_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    testfile.write_text(content)
    content_read = zt.get_string_from_file_content(test_dir, "test.md")
    assert content == content_read


def test_overwrite_file_content(tmp_path):
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    testfile = test_dir / "test.md"
    content = "abc"
    testfile.write_text(content)
    zt.overwrite_file_content(test_dir, "test.md", "def")
    content_read = zt.get_string_from_file_content(test_dir, "test.md")
    assert content_read == "def"
