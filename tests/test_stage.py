# test_stage.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import tools4zettelkasten as zt


def test_process_txt_file(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.persistency.PersistencyManager(tmp_path / "subdir")
    testfile = test_sub_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    testfile.write_text(content)
    zt.stage.process_txt_file(persistency_manager, "test.md")
    comparefile = test_sub_dir / "Eine_laengere_Ueberschrift.md"
    assert comparefile.exists()


def test_process_files_from_input(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.persistency.PersistencyManager(tmp_path / "subdir")
    first_testfile = test_sub_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    first_testfile.write_text(content)
    second_testfile = test_sub_dir / "other.txt"
    content = """# A very different topic

    and also some different content"""
    second_testfile.write_text(content)
    zt.stage.process_files_from_input(persistency_manager)
    first_comparefile = test_sub_dir / "Eine_laengere_Ueberschrift.md"
    second_comparefile = test_sub_dir / "A_very_different_topic.md"
    assert first_comparefile.exists()
    assert second_comparefile.exists()


def test_process_files_from_input_with_error(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.persistency.PersistencyManager(tmp_path / "subdir")
    first_testfile = test_sub_dir / "test.md"
    # Has no valid header and should lead to error
    content = """- Eine längere Überschrift

    and some content"""
    first_testfile.write_text(content)
    second_testfile = test_sub_dir / "other.txt"
    content = """# A very different topic

    and also some different content"""
    second_testfile.write_text(content)
    zt.stage.process_files_from_input(persistencyManager=persistency_manager)
    # First file should not be changed
    first_comparefile = test_sub_dir / "test.md"
    second_comparefile = test_sub_dir / "A_very_different_topic.md"
    assert first_comparefile.exists()
    assert second_comparefile.exists()


def test_process_files_from_input_with_existing_id(tmp_path):
    test_sub_dir = tmp_path / "subdir"
    test_sub_dir.mkdir()
    persistency_manager = zt.persistency.PersistencyManager(tmp_path / "subdir")
    first_testfile = test_sub_dir / "test.md"
    content = """# Eine längere Überschrift

    and some content"""
    first_testfile.write_text(content)
    second_testfile = test_sub_dir / "04_10_Some_Old_Topic_123456789.md"
    content = """# A very different topic

    and also some different content"""
    second_testfile.write_text(content)
    zt.stage.process_files_from_input(persistency_manager)
    first_comparefile = test_sub_dir / "Eine_laengere_Ueberschrift.md"
    second_comparefile = (
        test_sub_dir / "04_10_A_very_different_topic_123456789.md")
    assert first_comparefile.exists()
    assert second_comparefile.exists()
