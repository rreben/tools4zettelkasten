# test_stage.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import zettelkasten_tools as zt
import re


def test_process_txt_file(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    testfile = test_sub_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    testfile.write_text(content)
    zt.stage.process_txt_file(str(test_sub_dir), "test.md")
    comparefile = test_sub_dir / "Eine_laengere_Ueberschrift.md"
    assert comparefile.exists()


def test_process_files_from_input(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    first_testfile = test_sub_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    first_testfile.write_text(content)
    second_testfile = test_sub_dir / "other.txt"
    content = """# A very different topic

    and also some different content"""
    second_testfile.write_text(content)
    zt.stage.process_files_from_input(str(test_sub_dir))
    first_comparefile = test_sub_dir / "Eine_laengere_Ueberschrift.md"
    second_comparefile = test_sub_dir / "A_very_different_topic.md"
    assert first_comparefile.exists()
    assert second_comparefile.exists()
