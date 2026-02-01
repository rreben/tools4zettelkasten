# test_flask_views.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

"""Tests for Flask views including the SVG graph visualization."""

import pytest
from .context import tools4zettelkasten as zt


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from tools4zettelkasten.flask_views import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


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
