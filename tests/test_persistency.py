# test_persistency.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from zettelkasten_tools.persistency import list_of_filenames_from_directory
from .context import zettelkasten_tools as zt
import re


def test_create_file(tmpdir):
    """Creates a temporary test file and reads it back in

    The test uses the standard fixture in pytest to work
    with test files
    The fixture is described in
    https://docs.pytest.org/en/6.2.x/tmpdir.html

    :param tmpdir: this parameter is set as test fixture
                   by the pytest system
    :type tmpdir: directory
    """
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    assert p.read() == "content"
    assert len(tmpdir.listdir()) == 1


def test_rename_file(tmp_path):
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()
    testfile = test_dir / "test.md"
    testfile.write_text("some info")
    zt.rename_file(str(test_dir), "test.md", "new.md")
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
