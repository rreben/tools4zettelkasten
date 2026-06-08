# test_mcp_stage.py
# Tests for MCP stage_file full staging (parity with CLI `stage --fully`).

import os
import re

import pytest

# mcp_server requires the mcp package (Python 3.10+)
try:
    import tools4zettelkasten.mcp_server as mcp_module
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

requires_mcp = pytest.mark.skipif(
    not HAS_MCP, reason="mcp package not installed (requires Python 3.10+)")


@pytest.fixture
def tmp_input(tmp_path, monkeypatch):
    """Create a temporary input folder and point settings at it.

    Provides:
    - aaa.md            -> "# Mein Titel"
    - umlaut.md         -> "# Über Ärger"
    - ohne_header.md    -> no markdown header
    """
    import tools4zettelkasten.settings as st

    (tmp_path / "aaa.md").write_text("# Mein Titel\n\nsome content")
    (tmp_path / "umlaut.md").write_text("# Über Ärger\n\nsome content")
    (tmp_path / "ohne_header.md").write_text("- no header here\n\ncontent")

    monkeypatch.setattr(st, "ZETTELKASTEN_INPUT", str(tmp_path))
    return tmp_path


@requires_mcp
def test_stage_file_fully(tmp_input):
    res = mcp_module.stage_file("aaa.md")  # fully=True (default)
    assert res["success"] is True
    assert re.match(r"^0_0_Mein_Titel_[0-9a-f]{9}\.md$", res["new_name"])
    assert res["message"] == "Staged"
    # old file gone, new file present
    assert not os.path.exists(os.path.join(tmp_input, "aaa.md"))
    assert os.path.exists(os.path.join(tmp_input, res["new_name"]))


@requires_mcp
def test_stage_file_not_fully(tmp_input):
    res = mcp_module.stage_file("aaa.md", fully=False)
    assert res["success"] is True
    assert res["new_name"] == "Mein_Titel.md"
    assert os.path.exists(os.path.join(tmp_input, "Mein_Titel.md"))


@requires_mcp
def test_stage_file_idempotent(tmp_input):
    first = mcp_module.stage_file("aaa.md")["new_name"]
    second = mcp_module.stage_file(first)  # already a valid name
    assert second["new_name"] == first
    assert second["message"] == "No rename needed"
    assert second["old_name"] == first


@requires_mcp
def test_stage_file_no_header(tmp_input):
    res = mcp_module.stage_file("ohne_header.md")
    assert res["success"] is False
    assert "header" in res["error"].lower()


@requires_mcp
def test_stage_file_not_found(tmp_input):
    res = mcp_module.stage_file("does_not_exist.md")
    assert res["success"] is False
    assert "not found" in res["error"].lower()


@requires_mcp
def test_stage_file_umlaut_transliteration(tmp_input):
    res = mcp_module.stage_file("umlaut.md")
    assert res["success"] is True
    assert re.match(r"^0_0_Ueber_Aerger_[0-9a-f]{9}\.md$", res["new_name"])


@requires_mcp
def test_stage_file_id_pattern_only(tmp_input):
    """ID is timestamp-seeded; only its 9-hex-char pattern is asserted."""
    res = mcp_module.stage_file("aaa.md")
    # the id is the last underscore-separated token before .md
    file_id = res["new_name"][:-len(".md")].split("_")[-1]
    assert re.match(r"^[0-9a-f]{9}$", file_id)


@requires_mcp
def test_stage_all(tmp_input):
    results = mcp_module.stage_all()
    # Two files have valid headers, one (ohne_header.md) does not.
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    assert len(successes) == 2
    assert len(failures) == 1
    for r in successes:
        assert re.match(r"^0_0_[A-Za-z0-9_]+_[0-9a-f]{9}\.md$", r["new_name"])


@requires_mcp
def test_preview_staging_fully(tmp_input):
    changes = mcp_module.preview_staging()  # fully=True (default)
    by_old = {c["old_name"]: c for c in changes}
    assert by_old["aaa.md"]["new_name"] == "0_0_Mein_Titel_<id>.md"
    assert "note" in by_old["aaa.md"]
    # preview makes no changes on disk
    assert os.path.exists(os.path.join(tmp_input, "aaa.md"))


@requires_mcp
def test_preview_staging_not_fully(tmp_input):
    changes = mcp_module.preview_staging(fully=False)
    by_old = {c["old_name"]: c for c in changes}
    assert by_old["aaa.md"]["new_name"] == "Mein_Titel.md"
    assert "note" not in by_old["aaa.md"]


@requires_mcp
def test_list_input_files_after_staging(tmp_input):
    mcp_module.stage_file("aaa.md")
    files = mcp_module.list_input_files()
    staged = [f for f in files if f["filename"].startswith("0_0_Mein_Titel_")]
    assert len(staged) == 1
    entry = staged[0]
    assert entry["has_id"] is True
    assert entry["has_ordering"] is True
    assert entry["ordering"] == "0_0"
