# test_mcp_server.py
# Regression tests for MCP server integration (REQ-1 through REQ-8)

import pytest
import logging
from pathlib import Path

from .context import tools4zettelkasten as zt

# Check if mcp is available (requires Python 3.10+)
try:
    import tools4zettelkasten.mcp_server as mcp_module
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

requires_mcp = pytest.mark.skipif(
    not HAS_MCP, reason="mcp package not installed (requires Python 3.10+)")


# ---------------------------------------------------------------------------
# TEST-1: __init__.py namespace cleanliness (REQ-1 regression guard)
# ---------------------------------------------------------------------------

def test_init_does_not_export_cli_internals():
    """Test that __init__.py does not pollute namespace with CLI internals.

    The old __init__.py had 'from .cli import *' which pulled Click commands,
    dataclasses and helper functions into the package namespace.
    """
    # CLI-internal names that were previously exported via 'from .cli import *':
    assert not hasattr(zt, 'batch_rename')
    assert not hasattr(zt, 'batch_replace')
    assert not hasattr(zt, 'Rename_command')
    assert not hasattr(zt, 'show_banner')
    assert not hasattr(zt, 'messages')


# ---------------------------------------------------------------------------
# TEST-7: overwrite_settings in settings module (REQ-3)
# ---------------------------------------------------------------------------

def test_overwrite_settings_in_settings_module(monkeypatch):
    """Test that overwrite_settings lives in settings.py and works."""
    import tools4zettelkasten.settings as st
    assert hasattr(st, 'overwrite_settings')
    assert hasattr(st, 'overwrite_setting')

    monkeypatch.setenv('ZETTELKASTEN', '/custom/path')
    st.overwrite_settings()
    assert st.ZETTELKASTEN == '/custom/path'


# ---------------------------------------------------------------------------
# TEST-8: check_directories strict mode (REQ-8)
# ---------------------------------------------------------------------------

def test_check_directories_strict_mode(monkeypatch):
    """Test that check_directories in strict mode exits on missing dir."""
    import tools4zettelkasten.settings as st
    assert hasattr(st, 'check_directories')

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/nonexistent/path')
    with pytest.raises(SystemExit):
        st.check_directories(strict=True)


# ---------------------------------------------------------------------------
# TEST-9: check_directories non-strict mode (REQ-8)
# ---------------------------------------------------------------------------

def test_check_directories_non_strict_mode(monkeypatch, caplog):
    """Test that check_directories in non-strict mode only warns."""
    import tools4zettelkasten.settings as st

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/nonexistent/path')
    monkeypatch.setattr(st, 'ZETTELKASTEN_INPUT', '/nonexistent/input')
    monkeypatch.setattr(st, 'ZETTELKASTEN_IMAGES', '/nonexistent/images')
    with caplog.at_level(logging.WARNING):
        st.check_directories(strict=False)  # Should NOT exit
    assert '/nonexistent/path' in caplog.text


# ---------------------------------------------------------------------------
# TEST-2: MCP server module exists (REQ-2)
# ---------------------------------------------------------------------------

@requires_mcp
def test_mcp_server_module_exists():
    """Test that mcp_server module can be imported and has run_server."""
    assert hasattr(mcp_module, 'run_server')


# ---------------------------------------------------------------------------
# TEST-3: MCP server uses central settings (REQ-3)
# ---------------------------------------------------------------------------

@requires_mcp
def test_mcp_server_uses_settings(monkeypatch):
    """Test that MCP server reads paths from settings module."""
    import tools4zettelkasten.settings as st

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/test/mycelium')
    monkeypatch.setattr(st, 'ZETTELKASTEN_INPUT', '/test/input')

    manager = mcp_module.get_zettelkasten_manager()
    assert str(manager.directory) == '/test/mycelium'

    input_manager = mcp_module.get_input_manager()
    assert str(input_manager.directory) == '/test/input'


# ---------------------------------------------------------------------------
# TEST-4: mcp CLI command registered (REQ-4)
# ---------------------------------------------------------------------------

def test_mcp_cli_command_exists():
    """Test that mcp command is registered in CLI."""
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'mcp' in result.output


# ---------------------------------------------------------------------------
# TEST-5: All 12 MCP tools are registered (REQ-2)
# ---------------------------------------------------------------------------

@requires_mcp
def test_mcp_tools_registered():
    """Test that all 12 MCP tools are registered."""
    import asyncio

    expected_tools = [
        'list_input_files', 'preview_staging', 'stage_file',
        'get_zettel', 'search_zettel', 'list_zettel', 'get_statistics',
        'get_links', 'find_related', 'analyze_structure',
        'preview_reorganize', 'execute_reorganize'
    ]
    mcp_instance = mcp_module.mcp
    tool_list = asyncio.get_event_loop().run_until_complete(mcp_instance.list_tools())
    registered_names = [tool.name for tool in tool_list]
    for tool_name in expected_tools:
        assert tool_name in registered_names, f"Tool {tool_name} not registered"


# ---------------------------------------------------------------------------
# TEST-6: No importlib hack (REQ-2 regression guard)
# ---------------------------------------------------------------------------

def test_mcp_server_no_importlib():
    """Test that mcp_server.py does not use importlib hack."""
    server_path = Path(__file__).parent.parent / 'tools4zettelkasten' / 'mcp_server.py'
    server_code = server_path.read_text()
    assert 'importlib' not in server_code
