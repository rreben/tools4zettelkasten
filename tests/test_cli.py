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

    persistency_manager = zt.persistency.PersistencyManager(test_dir)

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

    persistency_manager = zt.persistency.PersistencyManager(test_dir)

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

    persistency_manager = zt.persistency.PersistencyManager(test_dir)

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

    persistency_manager = zt.persistency.PersistencyManager(test_dir)

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


# Tests for settings command (TEST-1 through TEST-7)

def test_settings_command_exists():
    """TEST-1: Test that settings command is registered"""
    from click.testing import CliRunner
    runner = CliRunner()
    # We need to mock the environment and directories to avoid early exit
    import os
    env = os.environ.copy()
    env['ZETTELKASTEN'] = '/tmp'
    env['ZETTELKASTEN_INPUT'] = '/tmp'
    env['ZETTELKASTEN_IMAGES'] = '/tmp'
    result = runner.invoke(zt.cli.messages, ['settings'], env=env)
    assert result.exit_code == 0


def test_settings_shows_version(capsys, monkeypatch):
    """TEST-2: Test that settings displays version"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setattr('os.path.isfile', lambda x: False)

    zt.cli.format_settings_output()

    captured = capsys.readouterr()
    assert zt.__version__ in captured.out


def test_settings_shows_paths(capsys, monkeypatch):
    """TEST-3: Test that settings displays all configured paths"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setattr('os.path.isfile', lambda x: False)

    zt.cli.format_settings_output()

    captured = capsys.readouterr()
    assert 'Zettelkasten' in captured.out
    assert 'Input' in captured.out
    assert 'Images' in captured.out


def test_settings_validates_existing_path(capsys, monkeypatch):
    """TEST-4: Test that existing paths show checkmark"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setattr('os.path.isfile', lambda x: False)

    zt.cli.format_settings_output()

    captured = capsys.readouterr()
    assert '✓' in captured.out


def test_settings_validates_missing_path(capsys, monkeypatch):
    """TEST-5: Test that missing paths show X mark"""
    monkeypatch.setattr('os.path.isdir', lambda x: False)
    monkeypatch.setattr('os.path.isfile', lambda x: False)

    zt.cli.format_settings_output()

    captured = capsys.readouterr()
    assert '✗' in captured.out


def test_settings_shows_env_var_status(capsys, monkeypatch):
    """TEST-6: Test that environment variable status is shown"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setattr('os.path.isfile', lambda x: False)

    zt.cli.format_settings_output()

    captured = capsys.readouterr()
    assert 'ENVIRONMENT' in captured.out


def test_show_command_removed():
    """TEST-7: Test that old show command no longer exists"""
    from click.testing import CliRunner
    runner = CliRunner()
    import os
    env = os.environ.copy()
    env['ZETTELKASTEN'] = '/tmp'
    env['ZETTELKASTEN_INPUT'] = '/tmp'
    env['ZETTELKASTEN_IMAGES'] = '/tmp'
    result = runner.invoke(zt.cli.messages, ['show'], env=env)
    assert result.exit_code != 0  # Command should not be found


def test_check_path_exists_with_directory(tmp_path):
    """Test check_path_exists returns True for existing directory"""
    assert zt.cli.check_path_exists(str(tmp_path)) is True


def test_check_path_exists_with_file(tmp_path):
    """Test check_path_exists returns True for existing file"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert zt.cli.check_path_exists(str(test_file)) is True


def test_check_path_exists_with_nonexistent():
    """Test check_path_exists returns False for non-existent path"""
    assert zt.cli.check_path_exists('/nonexistent/path/12345') is False


def test_get_env_var_status_set(monkeypatch):
    """Test get_env_var_status returns True for set variable"""
    monkeypatch.setenv('TEST_VAR', '/some/path')
    is_set, value = zt.cli.get_env_var_status('TEST_VAR')
    assert is_set is True
    assert value == '/some/path'


def test_get_env_var_status_not_set(monkeypatch):
    """Test get_env_var_status returns False for unset variable"""
    monkeypatch.delenv('NONEXISTENT_VAR', raising=False)
    is_set, value = zt.cli.get_env_var_status('NONEXISTENT_VAR')
    assert is_set is False
    assert value is None
