# test_cli.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import tools4zettelkasten as zt


def test_rename_command_dataclass():
    """Test Rename_command dataclass creation and attributes"""
    cmd = zt.cli.Rename_command(
        old_filename='old_file.md',
        new_filename='new_file.md'
    )
    assert cmd.old_filename == 'old_file.md'
    assert cmd.new_filename == 'new_file.md'
    assert isinstance(cmd, zt.cli.Command)


def test_batch_rename_executes_all_commands(tmp_path, monkeypatch):
    """Test that batch_rename executes all rename commands in order"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    # Create test files
    (test_dir / "old1.md").write_text("content1")
    (test_dir / "old2.md").write_text("content2")
    (test_dir / "old3.md").write_text("content3")

    persistency_manager = zt.PersistencyManager(test_dir)

    commands = [
        zt.cli.Rename_command('old1.md', 'new1.md'),
        zt.cli.Rename_command('old2.md', 'new2.md'),
        zt.cli.Rename_command('old3.md', 'new3.md'),
    ]

    # Mock the prompt to return True
    monkeypatch.setattr('tools4zettelkasten.cli.prompt',
                        lambda x: {'proceed': True})

    zt.cli.batch_rename(commands, persistency_manager)

    # Verify all files were renamed
    assert (test_dir / "new1.md").exists()
    assert (test_dir / "new2.md").exists()
    assert (test_dir / "new3.md").exists()
    assert not (test_dir / "old1.md").exists()
    assert not (test_dir / "old2.md").exists()
    assert not (test_dir / "old3.md").exists()


def test_batch_rename_preserves_order(tmp_path, monkeypatch):
    """Test that batch_rename preserves execution order"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    # Create initial file
    (test_dir / "file_a.md").write_text("content")

    persistency_manager = zt.PersistencyManager(test_dir)

    # Track execution order
    execution_order = []

    original_rename = persistency_manager.rename_file

    def tracking_rename(old, new):
        execution_order.append((old, new))
        original_rename(old, new)

    persistency_manager.rename_file = tracking_rename
    monkeypatch.setattr('tools4zettelkasten.cli.prompt',
                        lambda x: {'proceed': True})

    # Chained renames that depend on order:
    # file_a -> file_b -> file_c
    # This only works if order is preserved
    commands = [
        zt.cli.Rename_command('file_a.md', 'file_b.md'),
        zt.cli.Rename_command('file_b.md', 'file_c.md'),
    ]

    zt.cli.batch_rename(commands, persistency_manager)

    assert execution_order == [
        ('file_a.md', 'file_b.md'),
        ('file_b.md', 'file_c.md')
    ]
    assert (test_dir / "file_c.md").exists()


def test_batch_rename_aborts_on_decline(tmp_path, monkeypatch):
    """Test that batch_rename does nothing when user declines"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    (test_dir / "old.md").write_text("content")

    persistency_manager = zt.PersistencyManager(test_dir)

    commands = [
        zt.cli.Rename_command('old.md', 'new.md'),
    ]

    # Mock the prompt to return False
    monkeypatch.setattr('tools4zettelkasten.cli.prompt',
                        lambda x: {'proceed': False})

    zt.cli.batch_rename(commands, persistency_manager)

    # Original file should still exist
    assert (test_dir / "old.md").exists()
    assert not (test_dir / "new.md").exists()


def test_batch_rename_empty_list(tmp_path, monkeypatch):
    """Test that batch_rename handles empty command list gracefully"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    persistency_manager = zt.PersistencyManager(test_dir)

    # Track if prompt was called
    prompt_called = []

    def mock_prompt(x):
        prompt_called.append(True)
        return {'proceed': True}

    monkeypatch.setattr('tools4zettelkasten.cli.prompt', mock_prompt)

    zt.cli.batch_rename([], persistency_manager)

    # Prompt should not have been called
    assert len(prompt_called) == 0


def test_format_rename_output(capsys):
    """Test the formatted output of rename commands"""
    commands = [
        zt.cli.Rename_command(
            '1_5_another_Thought_2af216153.md',
            '1_2_another_Thought_2af216153.md'
        ),
    ]

    zt.cli.format_rename_output(commands)

    captured = capsys.readouterr()
    assert '1_5_another_Thought_2af216153.md' in captured.out
    assert '1_2_another_Thought_2af216153.md' in captured.out
    assert '1.' in captured.out  # Nummer der Umbenennung
    assert 'Geplante Umbenennungen (1)' in captured.out


def test_format_rename_output_empty_list(capsys):
    """Test format_rename_output with empty list"""
    zt.cli.format_rename_output([])

    captured = capsys.readouterr()
    assert 'Keine Umbenennungen erforderlich' in captured.out
