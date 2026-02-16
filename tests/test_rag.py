# test_rag.py
# Copyright (c) 2024 Dr. Rupert Rebentisch
# Licensed under the MIT license

import pytest
from .context import tools4zettelkasten as zt

# --- Tests for normalize_content and compute_content_hash ---
# These have no external dependencies and always run.

try:
    from tools4zettelkasten.rag import (
        normalize_content, compute_content_hash)
    HAS_RAG_CORE = True
except ImportError:
    HAS_RAG_CORE = False

try:
    from tools4zettelkasten.rag import VectorStore, ZettelkastenEmbedder
    import chromadb  # noqa
    HAS_RAG_DEPS = True
except ImportError:
    HAS_RAG_DEPS = False


# --- TEST-1 ---
@pytest.mark.skipif(not HAS_RAG_CORE, reason="rag module not importable")
def test_normalize_content_replaces_links():
    """Link-Dateinamen werden durch IDs ersetzt."""
    content = "See [note](01_12a_How_to_integrate_e0d27e3ad.md) for details."
    normalized = normalize_content(content)
    assert "e0d27e3ad" in normalized
    assert "01_12a" not in normalized


# --- TEST-2 ---
@pytest.mark.skipif(not HAS_RAG_CORE, reason="rag module not importable")
def test_normalize_content_preserves_non_links():
    """Nicht-Link-Inhalte bleiben unverändert."""
    content = "# Titel\n\nEin normaler Absatz ohne Links."
    assert normalize_content(content) == content


# --- TEST-3 ---
@pytest.mark.skipif(not HAS_RAG_CORE, reason="rag module not importable")
def test_normalize_content_handles_image_links():
    """Bild-Links (mit !) werden nicht verändert."""
    content = "![Bild](images/screenshot.png)"
    assert normalize_content(content) == content


# --- TEST-4 ---
@pytest.mark.skipif(not HAS_RAG_CORE, reason="rag module not importable")
def test_content_hash_stable_after_reorganize():
    """Content-Hash ändert sich nicht nach reorganize."""
    before = "See [note](01_12a_How_to_integrate_e0d27e3ad.md) for details."
    after = "See [note](01_13_How_to_integrate_e0d27e3ad.md) for details."
    assert compute_content_hash(before) == compute_content_hash(after)


# --- TEST-5 ---
@pytest.mark.skipif(not HAS_RAG_CORE, reason="rag module not importable")
def test_content_hash_changes_on_real_edit():
    """Content-Hash ändert sich bei echten inhaltlichen Änderungen."""
    original = "# Titel\n\nErster Absatz."
    edited = "# Titel\n\nErster Absatz mit Ergänzung."
    assert compute_content_hash(original) != compute_content_hash(edited)


# --- TEST-6 ---
@pytest.mark.skipif(not HAS_RAG_DEPS, reason="RAG dependencies not installed")
def test_sync_adds_new_zettel(tmp_path):
    """Neue Zettel werden zur Vektor-DB hinzugefügt."""
    zettel_dir = tmp_path / "mycelium"
    zettel_dir.mkdir()
    chroma_dir = tmp_path / "chroma"

    f1 = zettel_dir / "01_01_Test_Topic_a1b2c3d4e.md"
    f1.write_text("# Test Topic\n\nSome content about testing.")
    f2 = zettel_dir / "01_02_Another_Topic_f5e6d7c8b.md"
    f2.write_text("# Another Topic\n\nMore content here.")

    pm = zt.persistency.PersistencyManager(zettel_dir)
    store = VectorStore(chroma_path=str(chroma_dir))
    result = store.sync(pm)

    assert result.added == 2
    assert result.updated == 0
    assert result.deleted == 0


# --- TEST-7 ---
@pytest.mark.skipif(not HAS_RAG_DEPS, reason="RAG dependencies not installed")
def test_sync_detects_unchanged_after_reorganize(tmp_path):
    """Nach reorganize werden Zettel als unverändert erkannt."""
    zettel_dir = tmp_path / "mycelium"
    zettel_dir.mkdir()
    chroma_dir = tmp_path / "chroma"

    f1 = zettel_dir / "01_12a_Topic_a1b2c3d4e.md"
    f1.write_text("# Topic\n\nContent with [link](01_05_Other_f5e6d7c8b.md).")

    pm = zt.persistency.PersistencyManager(zettel_dir)
    store = VectorStore(chroma_path=str(chroma_dir))

    # First sync
    result1 = store.sync(pm)
    assert result1.added == 1

    # Simulate reorganize: rename file, update link target
    f1.unlink()
    f2 = zettel_dir / "01_13_Topic_a1b2c3d4e.md"
    f2.write_text("# Topic\n\nContent with [link](01_06_Other_f5e6d7c8b.md).")

    # Second sync — content hash should be the same
    pm2 = zt.persistency.PersistencyManager(zettel_dir)
    result2 = store.sync(pm2)
    assert result2.added == 0
    assert result2.updated == 0
    assert result2.metadata_updated == 1


# --- TEST-8 ---
@pytest.mark.skipif(not HAS_RAG_DEPS, reason="RAG dependencies not installed")
def test_search_returns_relevant_results(tmp_path):
    """Suche findet semantisch relevante Zettel."""
    zettel_dir = tmp_path / "mycelium"
    zettel_dir.mkdir()
    chroma_dir = tmp_path / "chroma"

    (zettel_dir / "01_01_Kreativitaet_a1b2c3d4e.md").write_text(
        "# Kreativität\n\nKreativität entsteht durch neue Kombinationen "
        "von bestehenden Ideen.")
    (zettel_dir / "01_02_Programmierung_f5e6d7c8b.md").write_text(
        "# Programmierung\n\nPython ist eine interpretierte "
        "Programmiersprache.")

    pm = zt.persistency.PersistencyManager(zettel_dir)
    store = VectorStore(chroma_path=str(chroma_dir))
    store.sync(pm)

    results = store.search("Wie entsteht Innovation?", top_k=2)
    assert len(results) == 2
    # The creativity zettel should be more relevant
    assert results[0].zettel_id == "a1b2c3d4e"


# --- TEST-9 ---
@pytest.mark.skipif(not HAS_RAG_DEPS, reason="RAG dependencies not installed")
def test_sync_removes_deleted_zettel(tmp_path):
    """Gelöschte Zettel werden aus der Vektor-DB entfernt."""
    zettel_dir = tmp_path / "mycelium"
    zettel_dir.mkdir()
    chroma_dir = tmp_path / "chroma"

    f1 = zettel_dir / "01_01_Topic_a1b2c3d4e.md"
    f1.write_text("# Topic\n\nContent.")

    pm = zt.persistency.PersistencyManager(zettel_dir)
    store = VectorStore(chroma_path=str(chroma_dir))
    store.sync(pm)

    # Delete the file
    f1.unlink()

    pm2 = zt.persistency.PersistencyManager(zettel_dir)
    result = store.sync(pm2)
    assert result.deleted == 1
    assert store.get_stats()['total_documents'] == 0


# --- TEST-10 ---
def test_vectorize_cli_command_exists():
    """Der vectorize-Befehl ist registriert."""
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'vectorize' in result.output


# --- TEST-11 ---
def test_chat_cli_command_exists():
    """Der chat-Befehl ist registriert."""
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'chat' in result.output
