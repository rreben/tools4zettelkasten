# test_collection_export.py
# Copyright (c) 2026 Dr. Rupert Rebentisch
# Licensed under the MIT license

"""Tests for the collection and its PDF (print view) / Markdown export."""

import pytest

PARENT = '01_Parent_aaaaaaaaa.md'
CHILD = '01_01_Child_bbbbbbbbb.md'
OTHER = '02_Other_ccccccccc.md'


@pytest.fixture
def zettelkasten_dir(tmp_path):
    """Create a temporary Zettelkasten with a parent, a child and a sibling."""
    (tmp_path / PARENT).write_text(
        '# Parent\n'
        '\n'
        'A note linking to [the child](' + CHILD + ') '
        'and to [an outsider](' + OTHER + ').\n')
    (tmp_path / CHILD).write_text(
        '# Child\n'
        '\n'
        '## Detail\n'
        '\n'
        '![A picture](images/picture.png)\n')
    (tmp_path / OTHER).write_text(
        '# Other\n'
        '\n'
        'An unrelated note.\n')
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
def read_only(monkeypatch):
    from tools4zettelkasten import settings as st
    monkeypatch.setattr(st, 'READ_ONLY', True)


def get_html(response):
    return response.data.decode('utf-8')


# Helper functions

def test_title_from_filename_strips_ordering_and_id():
    from tools4zettelkasten.flask_views import title_from_filename
    assert title_from_filename(PARENT) == 'Parent'
    assert title_from_filename(CHILD) == 'Child'
    assert title_from_filename(
        '01_02_Some_Topic_fb134b00b.md') == 'Some Topic'


def test_extract_title_prefers_first_heading():
    from tools4zettelkasten.flask_views import extract_title
    assert extract_title('# The Title\n\nText\n', PARENT) == 'The Title'


def test_extract_title_falls_back_to_filename():
    from tools4zettelkasten.flask_views import extract_title
    assert extract_title('Just text\n', PARENT) == 'Parent'


def test_demote_headings_shifts_levels():
    from tools4zettelkasten.flask_views import demote_headings
    assert demote_headings('# One\n## Two\n') == '## One\n### Two'


def test_demote_headings_keeps_level_six_and_code_blocks():
    from tools4zettelkasten.flask_views import demote_headings
    source = '###### Six\n\n```\n# not a heading\n```\n'
    result = demote_headings(source)
    assert '###### Six' in result
    assert '# not a heading' in result
    assert '## not a heading' not in result


def test_anchor_for_filename():
    from tools4zettelkasten.flask_views import anchor_for_filename
    assert anchor_for_filename(PARENT) == 'note-01_Parent_aaaaaaaaa'


# Collection page

def test_collection_page_exists(client):
    response = client.get('/collection')
    assert response.status_code == 200
    html = get_html(response)
    assert 'js/collection.js' in html
    assert 'collection-entries' in html
    assert 'collection-empty' in html


def test_collection_page_has_export_options_and_buttons(client):
    html = get_html(client.get('/collection'))
    for name in ('title', 'toc', 'page_breaks', 'show_sources',
                 'demote_headings'):
        assert 'name="' + name + '"' in html
    assert '/collection/print' in html
    assert '/collection/markdown' in html


# Start page

def test_start_page_contains_collection_controls(client):
    html = get_html(client.get('/'))
    assert 'js/collection.js' in html
    assert 'data-collection-count' in html
    assert 'data-collection-toggle' in html
    assert 'data-filename="' + PARENT + '"' in html
    assert 'data-ordering="01"' in html
    assert 'data-ordering="01_01"' in html


def test_start_page_offers_subtree_only_where_descendants_exist(client):
    html = get_html(client.get('/'))
    assert 'data-collection-subtree' in html
    assert html.count('data-collection-subtree') == 1


# Note view

def test_note_view_contains_collection_toggle(client):
    html = get_html(client.get('/' + PARENT))
    assert 'data-collection-toggle' in html
    assert 'data-filename="' + PARENT + '"' in html
    assert 'js/collection.js' in html
    assert 't4zCollection.toggle' in html
    assert '/collection' in html


# Print export

def test_print_export_contains_notes_in_posted_order(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert '<h1>Parent</h1>' in html
    assert '<h1>Child</h1>' in html
    assert html.index('<h1>Parent</h1>') < html.index('<h1>Child</h1>')


def test_print_export_respects_reversed_order(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [CHILD, PARENT]}))
    assert html.index('<h1>Child</h1>') < html.index('<h1>Parent</h1>')


def test_print_export_contains_base_element_and_anchors(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert '<base href="/">' in html
    assert 'id="note-01_Parent_aaaaaaaaa"' in html
    assert 'id="note-01_01_Child_bbbbbbbbb"' in html


def test_print_export_keeps_relative_image_paths(client):
    html = get_html(client.post('/collection/print', data={'files': [CHILD]}))
    assert 'src="images/picture.png"' in html


def test_print_export_rewrites_links_between_collected_notes(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert 'href="#note-01_01_Child_bbbbbbbbb"' in html


def test_print_export_keeps_links_to_notes_outside_the_collection(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert 'href="' + OTHER + '"' in html
    assert 'note-02_Other_ccccccccc' not in html


def test_print_export_page_breaks_option(client):
    with_breaks = get_html(client.post(
        '/collection/print',
        data={'files': [PARENT, CHILD], 'page_breaks': '1'}))
    assert 'break-before: page' in with_breaks

    without_breaks = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert 'break-before: page' not in without_breaks


def test_print_export_toc_option(client):
    with_toc = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD], 'toc': '1'}))
    assert 'Contents' in with_toc
    assert 'href="#note-01_Parent_aaaaaaaaa"' in with_toc

    without_toc = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD]}))
    assert 'Contents' not in without_toc


def test_print_export_toc_shows_ordering_and_filename(client):
    html = get_html(client.post(
        '/collection/print', data={'files': [PARENT, CHILD], 'toc': '1'}))
    assert '01 &middot; Parent' in html
    assert '01_01 &middot; Child' in html
    assert PARENT in html
    assert CHILD in html


def test_print_export_title_option(client):
    html = get_html(client.post(
        '/collection/print',
        data={'files': [PARENT], 'title': 'My Excerpt'}))
    assert 'My Excerpt' in html


def test_print_export_show_sources_option(client):
    with_sources = get_html(client.post(
        '/collection/print',
        data={'files': [PARENT], 'show_sources': '1'}))
    assert PARENT in with_sources

    without_sources = get_html(client.post(
        '/collection/print', data={'files': [PARENT]}))
    assert '<p class="zettel-source">' not in without_sources


def test_print_export_demote_headings_option(client):
    html = get_html(client.post(
        '/collection/print',
        data={'files': [CHILD], 'demote_headings': '1'}))
    assert '<h2>Child</h2>' in html
    assert '<h3>Detail</h3>' in html
    assert '<h1>Child</h1>' not in html


def test_print_export_rejects_unknown_note(client):
    response = client.post(
        '/collection/print', data={'files': ['99_Nope_000000000.md']})
    assert response.status_code == 400


def test_print_export_rejects_path_traversal(client):
    response = client.post(
        '/collection/print', data={'files': ['../../etc/passwd']})
    assert response.status_code == 400


def test_print_export_rejects_empty_collection(client):
    response = client.post('/collection/print', data={})
    assert response.status_code == 400


# Markdown export

def test_markdown_export_returns_sources_in_order(client):
    response = client.post(
        '/collection/markdown', data={'files': [CHILD, PARENT]})
    assert response.status_code == 200
    body = response.data.decode('utf-8')
    assert body.index('# Child') < body.index('# Parent')
    assert '\n---\n' in body


def test_markdown_export_sets_download_headers(client):
    response = client.post(
        '/collection/markdown', data={'files': [PARENT]})
    assert 'text/markdown' in response.headers['Content-Type']
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'collection.md' in response.headers['Content-Disposition']


def test_markdown_export_filename_follows_title(client):
    response = client.post(
        '/collection/markdown',
        data={'files': [PARENT], 'title': 'Mein Auszug'})
    assert 'Mein_Auszug.md' in response.headers['Content-Disposition']


def test_markdown_export_title_and_sources(client):
    response = client.post(
        '/collection/markdown',
        data={'files': [PARENT], 'title': 'My Excerpt',
              'show_sources': '1'})
    body = response.data.decode('utf-8')
    assert body.startswith('# My Excerpt')
    assert '<!-- ' + PARENT + ' -->' in body


def test_markdown_export_demote_headings(client):
    response = client.post(
        '/collection/markdown',
        data={'files': [CHILD], 'demote_headings': '1'})
    body = response.data.decode('utf-8')
    assert '## Child' in body
    assert '### Detail' in body


def test_markdown_export_rejects_unknown_note(client):
    response = client.post(
        '/collection/markdown', data={'files': ['99_Nope_000000000.md']})
    assert response.status_code == 400


# Read-only mode

def test_exports_work_in_read_only_mode(client, read_only):
    assert client.post(
        '/collection/print',
        data={'files': [PARENT]}).status_code == 200
    assert client.post(
        '/collection/markdown',
        data={'files': [PARENT]}).status_code == 200
    assert client.get('/collection').status_code == 200


def test_collection_controls_available_in_read_only_mode(client, read_only):
    assert 'data-collection-toggle' in get_html(client.get('/'))
    assert 'data-collection-toggle' in get_html(client.get('/' + PARENT))


# Markdown features

def test_markdown_tables_are_rendered(client, zettelkasten_dir):
    """Pipe tables must become real tables, in the note view and the export."""
    table_note = '03_Table_ddddddddd.md'
    (zettelkasten_dir / table_note).write_text(
        '# Table\n'
        '\n'
        '| Column A | Column B |\n'
        '| -------- | -------- |\n'
        '| one      | two      |\n')

    html = get_html(client.get('/' + table_note))
    assert '<table>' in html
    assert '<th>Column A</th>' in html
    assert '<td>one</td>' in html

    export = get_html(client.post(
        '/collection/print', data={'files': [table_note]}))
    assert '<table>' in export
    assert '<th>Column A</th>' in export
