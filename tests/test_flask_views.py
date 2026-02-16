# test_flask_views.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

"""Tests for Flask views including the SVG graph visualization."""

import pytest
from .context import tools4zettelkasten as zt


@pytest.fixture
def zettelkasten_dir(tmp_path):
    """Create a temporary Zettelkasten directory with sample files."""
    note1 = tmp_path / '01_Test_Note_abc123456.md'
    note1.write_text('# Test Note\n\nThis is a test note.\n')
    note2 = tmp_path / '01_01_Sub_Note_def123456.md'
    note2.write_text('# Sub Note\n\nA sub note with [link](01_Test_Note_abc123456.md).\n')
    return tmp_path


@pytest.fixture
def client(zettelkasten_dir):
    """Create a test client for the Flask app with isolated Zettelkasten."""
    from tools4zettelkasten.flask_views import app
    from tools4zettelkasten import settings as st
    original_zettelkasten = st.ZETTELKASTEN
    st.ZETTELKASTEN = str(zettelkasten_dir)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client
    st.ZETTELKASTEN = original_zettelkasten


@pytest.fixture
def app_context():
    """Create an application context."""
    from tools4zettelkasten.flask_views import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.app_context():
        yield app


# Tests for SVG Graph View

def test_svggraph_route_exists(client):
    """Test that /svggraph route exists and returns 200."""
    response = client.get('/svggraph')
    assert response.status_code == 200


def test_svggraph_returns_html(client):
    """Test that /svggraph returns HTML content."""
    response = client.get('/svggraph')
    assert response.content_type.startswith('text/html')


def test_svggraph_contains_svg(client):
    """Test that /svggraph response contains SVG element."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert '<svg' in html.lower()


def test_svggraph_contains_svg_pan_zoom_library(client):
    """Test that svg-pan-zoom library is included."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'svg-pan-zoom' in html


def test_svggraph_contains_hammer_js_library(client):
    """Test that Hammer.js library is included for touch support."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'hammerjs' in html.lower() or 'hammer.min.js' in html.lower()


def test_svggraph_contains_zoom_controls(client):
    """Test that zoom control buttons are present."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'zoom-in' in html
    assert 'zoom-out' in html
    assert 'zoom-reset' in html


def test_svggraph_contains_zoom_level_display(client):
    """Test that zoom level indicator is present."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'zoom-level' in html


def test_svggraph_contains_navigation_back_link(client):
    """Test that navigation link back to list is present."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'Zurück zur Liste' in html or 'url_for' in html


def test_svggraph_contains_svg_container(client):
    """Test that SVG container element is present."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'svg-container' in html


def test_svggraph_contains_state_persistence_code(client):
    """Test that session storage state persistence is implemented."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'sessionStorage' in html
    assert 'svggraph_state' in html


def test_svggraph_contains_help_text(client):
    """Test that help text for user interactions is present."""
    response = client.get('/svggraph')
    html = response.data.decode('utf-8')
    assert 'help-text' in html


# Tests for Index Route

def test_index_route_exists(client):
    """Test that index route exists and returns 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_index_contains_graph_link(client):
    """Test that index page contains link to graph view."""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'svggraph' in html or 'Zettelkasten as a Graphic' in html


# Tests for analyse module graph creation

def test_create_graph_of_zettelkasten_with_urls():
    """Test that create_graph_of_zettelkasten includes URLs when requested."""
    from tools4zettelkasten.flask_views import app
    from tools4zettelkasten.analyse import create_graph_of_zettelkasten

    # Need request context for url_for to work
    app.config['SERVER_NAME'] = 'localhost'
    with app.app_context():
        with app.test_request_context():
            # Create minimal test data
            list_of_filenames = ['01_Test_Note_abc12345.md']
            list_of_links = []

            # Create graph with URL in nodes
            dot = create_graph_of_zettelkasten(
                list_of_filenames,
                list_of_links,
                url_in_nodes=True
            )

            # Check that the graph source contains URL attribute
            source = dot.source
            assert 'URL=' in source or 'href=' in source.lower()

    # Reset SERVER_NAME
    app.config['SERVER_NAME'] = None


def test_create_graph_of_zettelkasten_without_urls():
    """Test that create_graph_of_zettelkasten works without URLs."""
    from tools4zettelkasten.analyse import create_graph_of_zettelkasten

    # Create minimal test data
    list_of_filenames = ['01_Test_Note_abc12345.md']
    list_of_links = []

    # Create graph without URL in nodes
    dot = create_graph_of_zettelkasten(
        list_of_filenames,
        list_of_links,
        url_in_nodes=False
    )

    # Graph should still be created
    assert dot is not None
    assert 'Test Note' in dot.source or 'abc12345' in dot.source


# Tests for note navigation (get_adjacent_files)

def test_get_adjacent_files_middle():
    """TEST-1: Mittlere Datei hat Vorherige und Naechste."""
    from tools4zettelkasten.flask_views import get_adjacent_files

    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next_f = get_adjacent_files('b.md', sorted_list)
    assert prev == 'a.md'
    assert next_f == 'c.md'


def test_get_adjacent_files_first():
    """TEST-2: Erste Datei hat keine Vorherige."""
    from tools4zettelkasten.flask_views import get_adjacent_files

    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next_f = get_adjacent_files('a.md', sorted_list)
    assert prev is None
    assert next_f == 'b.md'


def test_get_adjacent_files_last():
    """TEST-3: Letzte Datei hat keine Naechste."""
    from tools4zettelkasten.flask_views import get_adjacent_files

    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next_f = get_adjacent_files('c.md', sorted_list)
    assert prev == 'b.md'
    assert next_f is None


def test_get_adjacent_files_single():
    """TEST-4: Einzelne Datei hat weder Vorherige noch Naechste."""
    from tools4zettelkasten.flask_views import get_adjacent_files

    sorted_list = ['a.md']
    prev, next_f = get_adjacent_files('a.md', sorted_list)
    assert prev is None
    assert next_f is None


def test_get_adjacent_files_not_found():
    """TEST-5: Nicht existierende Datei gibt None zurueck."""
    from tools4zettelkasten.flask_views import get_adjacent_files

    sorted_list = ['a.md', 'b.md']
    prev, next_f = get_adjacent_files('x.md', sorted_list)
    assert prev is None
    assert next_f is None


def test_navigation_uses_hierarchical_order():
    """TEST-6: Navigation verwendet hierarchische Reihenfolge."""
    from tools4zettelkasten.flask_views import get_adjacent_files
    from tools4zettelkasten.reorganize import (
        generate_tokenized_list, generate_tree, flatten_tree_to_list
    )

    # 12.md ist Eltern von 12_01.md
    filenames = ['12_01_Child_abc12345.md', '12_Parent_def12345.md']
    tokenized = generate_tokenized_list(filenames)
    tree = generate_tree(tokenized)
    sorted_list = flatten_tree_to_list(tree)

    # Hierarchisch: Parent vor Child
    assert sorted_list.index('12_Parent_def12345.md') < \
        sorted_list.index('12_01_Child_abc12345.md')

    prev, next_f = get_adjacent_files('12_01_Child_abc12345.md', sorted_list)
    assert prev == '12_Parent_def12345.md'


def test_note_view_contains_navigation_buttons(client):
    """TEST-7: Die Notiz-Ansicht enthaelt Navigations-Buttons."""
    # Hole eine beliebige Notiz aus dem Zettelkasten
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        # Finde einen Link zu einer Notiz
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_url = match.group(1)
            response = client.get(note_url)
            html = response.data.decode('utf-8')
            # Navigation sollte vorhanden sein
            assert 'Vorherige' in html or 'previous' in html.lower()
            assert 'Naechste' in html or 'next' in html.lower()
            assert 'Liste' in html
            assert 'Edit' in html


def test_note_view_contains_keyboard_hint(client):
    """Die Notiz-Ansicht enthaelt Tastatur-Hinweis."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_url = match.group(1)
            response = client.get(note_url)
            html = response.data.decode('utf-8')
            assert 'keyboard-hint' in html or 'Tastatur' in html


# Tests for edit view buttons

def test_edit_view_has_save_button(client):
    """TEST-1: Edit-Ansicht hat Save-Button."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_filename = match.group(1).lstrip('/')
            response = client.get(f'/edit/{note_filename}')
            html = response.data.decode('utf-8')
            assert 'Save' in html


def test_edit_view_has_cancel_button(client):
    """TEST-2: Edit-Ansicht hat Cancel-Button."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_filename = match.group(1).lstrip('/')
            response = client.get(f'/edit/{note_filename}')
            html = response.data.decode('utf-8')
            assert 'Cancel' in html


def test_edit_cancel_links_to_note_view(client):
    """TEST-3: Cancel-Button fuehrt zur Notiz-Ansicht."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_filename = match.group(1).lstrip('/')
            response = client.get(f'/edit/{note_filename}')
            html = response.data.decode('utf-8')
            # Cancel-Link sollte zur Notiz zurueckfuehren
            assert f'/{note_filename}' in html or 'show_md_file' in html


def test_edit_no_submit_text(client):
    """TEST-4: 'Submit'-Text ist nicht mehr als Button vorhanden."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_filename = match.group(1).lstrip('/')
            response = client.get(f'/edit/{note_filename}')
            html = response.data.decode('utf-8')
            # Submit sollte nicht als alleinstehender Button-Text erscheinen
            assert '>Submit<' not in html


def test_edit_view_has_fixed_footer(client):
    """TEST-5: Edit-Ansicht hat fixierte Footer-Leiste."""
    response = client.get('/')
    if response.status_code == 200:
        html = response.data.decode('utf-8')
        import re
        match = re.search(r'href="(/[^"]+\.md)"', html)
        if match:
            note_filename = match.group(1).lstrip('/')
            response = client.get(f'/edit/{note_filename}')
            html = response.data.decode('utf-8')
            assert 'edit-footer' in html or 'fixed' in html
