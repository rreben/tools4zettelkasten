# flask_views.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

from ast import Str
from flask import (
    Flask, render_template, send_from_directory, redirect, url_for, request,
    session, jsonify, abort)
from . import settings as st
from . import analyse as an
from . import reorganize as ro
from .persistency import PersistencyManager
from . import handle_filenames as hf
import markdown
import re
from pygments.formatters import HtmlFormatter
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from flask_pagedown import PageDown
import os

# After some attempts I initialize the app object in this file.
# The app object will be initialized in the import procedure of
# this file.
# I would have liked to have the initialization of all objects
# in the parent file, but I could not find a way to do that:
# Using url_map did not allow for parameters to be shared.
# Using Flask Blueprint did not work very well, because I would have
# to initialize the pagedown file in this file, also I loose the
# @app.route() decorator.
app = Flask(
        __name__, template_folder=st.TEMPLATE_FOLDER,
        static_folder=st.STATIC_FOLDER)

pagedown = PageDown(app)

# A configured key keeps sessions and CSRF tokens valid across WSGI workers
# and restarts; otherwise fall back to a random key per process.
app.config['SECRET_KEY'] = st.FLASK_SECRET_KEY or os.urandom(32)


@app.context_processor
def inject_read_only():
    return {'read_only': st.READ_ONLY}


class PageDownForm(FlaskForm):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Save')


def run_flask_server():
    """Run the flask server on port 5001.

    Port 5001 is used instead of the Flask default 5000
    because macOS Monterey and later use port 5000 for AirPlay Receiver.
    """
    app.debug = True
    print("Server running at http://127.0.0.1:5001/")
    app.run(host='127.0.0.1', port=5001)


def url_for_file(filename) -> Str:
    URL = url_for('show_md_file', file=filename)
    return URL


def get_adjacent_files(filename: str, sorted_list: list) -> tuple:
    """Ermittelt vorherige und nächste Datei in der hierarchischen Liste.

    :param filename: Aktuelle Datei
    :param sorted_list: Hierarchisch sortierte Dateiliste
    :return: Tuple (previous_file, next_file), None wenn nicht vorhanden
    """
    try:
        current_index = sorted_list.index(filename)
    except ValueError:
        return (None, None)

    previous_file = sorted_list[current_index - 1] if current_index > 0 else None
    next_file = sorted_list[current_index + 1] if current_index < len(sorted_list) - 1 else None

    return (previous_file, next_file)


def get_sorted_zettelkasten_list(persistencyManager: PersistencyManager) -> list:
    """Ermittelt die hierarchisch sortierte Liste aller Notizen.

    :param persistencyManager: PersistencyManager Instanz
    :return: Hierarchisch sortierte Liste der Dateinamen
    """
    zettelkasten_list = persistencyManager.get_list_of_filenames()
    tokenized_list = ro.generate_tokenized_list(zettelkasten_list)
    tree = ro.generate_tree(tokenized_list)
    return ro.flatten_tree_to_list(tree)


MARKDOWN_EXTENSIONS = [
    "fenced_code",
    'codehilite',
    'attr_list',
    # Pipe tables are not part of core markdown; without this extension a
    # table is rendered as literal | ... | text.
    'tables',
    'pymdownx.arithmatex',
]

MARKDOWN_EXTENSION_CONFIGS = {
    'pymdownx.arithmatex': {'generic': True}
}

# Links to other notes, as produced by the Zettelkasten conventions, e.g.
# <a href="01_02_Some_Topic_fb134b00b.md">
INTERNAL_LINK_REG_EX = re.compile(r'href="([^":/?#]+\.md)"')

# ATX headings that can still be demoted by one level (h6 is the deepest).
ATX_HEADING_REG_EX = re.compile(r'^(#{1,5})(\s|$)')


def render_markdown_to_html(markdown_string: str) -> str:
    """Render note markdown to HTML with the Zettelkasten extension set.

    :param markdown_string: The markdown source of a note
    :return: The rendered HTML fragment
    """
    return markdown.markdown(
        markdown_string, output_format='html5',
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS)


def get_code_css_string() -> str:
    """Return the Pygments style definitions wrapped in a style element."""
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    return "<style>" + formatter.get_style_defs() + "</style>"


def title_from_filename(filename: str) -> str:
    """Derive a readable title from a note filename.

    Ordering and id are stripped, underscores become spaces.

    :param filename: The filename of a note
    :return: A readable title
    """
    base_filename = hf.get_filename_components(filename)[1]
    return base_filename.replace('_', ' ').strip() or filename


def extract_title(markdown_string: str, filename: str) -> str:
    """Determine the title of a note.

    The first level-1 heading wins; otherwise the filename is used.

    :param markdown_string: The markdown source of a note
    :param filename: The filename of the note, used as fallback
    :return: The title of the note
    """
    for line in markdown_string.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return title_from_filename(filename)


def demote_headings(markdown_string: str) -> str:
    """Shift all ATX headings of a note down by one level.

    Headings inside fenced code blocks are left alone, and level 6 headings
    cannot be demoted any further.

    :param markdown_string: The markdown source of a note
    :return: The markdown source with demoted headings
    """
    lines = []
    in_fence = False
    for line in markdown_string.splitlines():
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            lines.append(line)
            continue
        if not in_fence and ATX_HEADING_REG_EX.match(line):
            lines.append('#' + line)
        else:
            lines.append(line)
    return '\n'.join(lines)


def anchor_for_filename(filename: str) -> str:
    """Return the in-document anchor id used for a note in the print view."""
    if filename.endswith('.md'):
        filename = filename[:-3]
    return 'note-' + filename


def rewrite_internal_links(html_string: str, collected: set) -> str:
    """Turn links between collected notes into in-document links.

    Links to notes that are part of the collection become anchor links, so
    that they keep working inside the exported document. Links to notes
    outside the collection are left untouched and keep pointing at the
    web UI.

    :param html_string: The rendered HTML of one note
    :param collected: The set of filenames in the collection
    :return: The HTML with rewritten links
    """
    def replace(match):
        target = match.group(1)
        if target in collected:
            return 'href="#' + anchor_for_filename(target) + '"'
        return match.group(0)

    return INTERNAL_LINK_REG_EX.sub(replace, html_string)


def get_collection_filenames(persistencyManager: PersistencyManager) -> list:
    """Read the posted collection and validate it against the Zettelkasten.

    Only filenames that really exist in the Zettelkasten are accepted. This
    also rejects path traversal attempts.

    :param persistencyManager: PersistencyManager instance
    :return: The posted filenames in the posted order
    """
    filenames = request.form.getlist('files')
    if not filenames:
        abort(400, description='No notes selected for export.')
    known_filenames = set(persistencyManager.get_list_of_filenames())
    for filename in filenames:
        if filename not in known_filenames:
            abort(400, description='Unknown note: ' + filename)
    return filenames


def get_collection_options() -> dict:
    """Read the export options from the posted form."""
    return {
        'title': request.form.get('title', '').strip(),
        'toc': 'toc' in request.form,
        'page_breaks': 'page_breaks' in request.form,
        'show_sources': 'show_sources' in request.form,
        'demote_headings': 'demote_headings' in request.form,
    }


def get_download_filename(title: str, extension: str) -> str:
    """Build a download filename from the export title."""
    base_filename = hf.create_base_filename_from_title(title) if title else ''
    return (base_filename or 'collection') + extension


def build_note_entries(sorted_list: list) -> list:
    """Enrich the hierarchically sorted filename list for the list view.

    The list view needs the ordering of each note (so that the browser can
    collect a whole subtree) and the information whether a note has
    descendants at all. Because the sorted list is depth first, the
    descendants of a note follow it directly, so it is enough to look at the
    next entry.

    :param sorted_list: Hierarchically sorted list of filenames
    :return: List of dictionaries describing the notes
    """
    orderings = [hf.get_filename_components(f)[0] for f in sorted_list]
    entries = []
    for index, filename in enumerate(sorted_list):
        ordering = orderings[index]
        next_ordering = (
            orderings[index + 1] if index + 1 < len(orderings) else '')
        entries.append({
            'filename': filename,
            'ordering': ordering,
            'title': title_from_filename(filename),
            'has_subtree': bool(ordering) and next_ordering.startswith(
                ordering + '_'),
        })
    return entries


@app.route('/')
def index():
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    zettelkasten_list = get_sorted_zettelkasten_list(persistencyManager)
    return render_template(
        'startpage.html',
        zettelkasten=build_note_entries(zettelkasten_list))


@app.route('/<file>')
def show_md_file(file):
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    filename = file

    # This route also catches requests that are not notes at all, for
    # example /favicon.ico or an image that a note references without the
    # images/ prefix. Those must not raise a FileNotFoundError (HTTP 500).
    if not persistencyManager.is_file_existing(filename):
        abort(404, description='No such note: ' + filename)

    # Hierarchisch sortierte Liste für Navigation ermitteln
    sorted_list = get_sorted_zettelkasten_list(persistencyManager)
    previous_file, next_file = get_adjacent_files(filename, sorted_list)

    input_file = persistencyManager.get_string_from_file_content(filename)
    htmlString = render_markdown_to_html(input_file)
    return render_template(
        "mainpage.html",
        codeCSSString=get_code_css_string(),
        htmlString=htmlString,
        filename=filename,
        previous_file=previous_file,
        next_file=next_file)


@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit(filename):
    if st.READ_ONLY:
        abort(403, description='Editing is disabled (read-only mode).')
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    input_file = persistencyManager.get_string_from_file_content(filename)
    markdown_string = input_file
    form = PageDownForm()
    form.pagedown.data = markdown_string
    if form.validate_on_submit():
        if request.method == 'POST':
            new_markdown_string = request.form['pagedown']
            form.pagedown.data = new_markdown_string
            persistencyManager.overwrite_file_content(
                filename, new_markdown_string)
            return redirect(url_for('show_md_file', file=filename))
    return render_template('edit.html', form=form, filename=filename)


@app.route('/images/<path:filename>')
def send_image(filename):
    # send_from_directory() resolves a relative directory against the app
    # root (the package directory), not against the working directory. A
    # configured path like ../zettelkasten/mycelium/images would therefore
    # never be found, so it is made absolute here.
    return send_from_directory(
        os.path.abspath(st.ZETTELKASTEN_IMAGES),
        filename)


@app.route('/svggraph')
def svggraph():
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    analysis = an.create_graph_analysis(
        persistencyManager)
    dot = an.create_graph_of_zettelkasten(
            analysis.list_of_filenames,
            analysis.list_of_links,
            url_in_nodes=True)
    chart_output = dot.pipe(format='svg').decode('utf-8')

    return render_template('visualzk.html', chart_output=chart_output)


@app.route('/chat', methods=['GET', 'POST'])
def chat_view():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('chat_view'))

        try:
            from . import rag
        except ImportError:
            session['chat_history'].append({
                'role': 'error',
                'content': "RAG dependencies not installed. "
                           "Install with: pip install 'tools4zettelkasten[rag]'"
            })
            return redirect(url_for('chat_view'))

        try:
            store = rag.VectorStore()
            search_results = store.search(query)
            conversation_history = []
            for msg in session['chat_history']:
                if msg['role'] in ('user', 'assistant'):
                    conversation_history.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            response = rag.chat_completion(
                query, search_results, conversation_history)
            sources = [
                {
                    'zettel_id': r.zettel_id,
                    'title': r.title,
                    'ordering': r.ordering,
                    'filename': r.filename,
                }
                for r in search_results
            ]
            session['chat_history'].append({
                'role': 'user', 'content': query})
            session['chat_history'].append({
                'role': 'assistant',
                'content': response,
                'sources': sources,
            })
            session.modified = True
        except Exception as e:
            session['chat_history'].append({
                'role': 'error', 'content': str(e)})
            session.modified = True

        return redirect(url_for('chat_view'))

    return render_template(
        'chat.html', chat_history=session.get('chat_history', []))


@app.route('/chat/reset', methods=['POST'])
def chat_reset():
    session.pop('chat_history', None)
    return redirect(url_for('chat_view'))


@app.route('/collection')
def collection():
    """Show the collection page.

    The collection itself lives in the browser (localStorage), so this view
    only renders the page shell; the entries are rendered by collection.js.
    """
    return render_template('collection.html')


@app.route('/collection/print', methods=['POST'])
def collection_print():
    """Render the collected notes as one printable document.

    The browser turns this view into a PDF ("Print" -> "Save as PDF"), which
    keeps formulas (MathJax), syntax highlighting and images intact.
    """
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    filenames = get_collection_filenames(persistencyManager)
    options = get_collection_options()
    collected = set(filenames)

    notes = []
    for filename in filenames:
        markdown_string = persistencyManager.get_string_from_file_content(
            filename)
        title = extract_title(markdown_string, filename)
        if options['demote_headings']:
            markdown_string = demote_headings(markdown_string)
        html_string = rewrite_internal_links(
            render_markdown_to_html(markdown_string), collected)
        notes.append({
            'filename': filename,
            'title': title,
            'ordering': hf.get_filename_components(filename)[0],
            'anchor': anchor_for_filename(filename),
            'html': html_string,
        })

    return render_template(
        'collection_print.html',
        codeCSSString=get_code_css_string(),
        notes=notes,
        options=options)


@app.route('/collection/markdown', methods=['POST'])
def collection_markdown():
    """Return the sources of the collected notes as a single markdown file."""
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    filenames = get_collection_filenames(persistencyManager)
    options = get_collection_options()

    parts = []
    for filename in filenames:
        markdown_string = persistencyManager.get_string_from_file_content(
            filename)
        if options['demote_headings']:
            markdown_string = demote_headings(markdown_string)
        part = ''
        if options['show_sources']:
            part += '<!-- ' + filename + ' -->\n\n'
        parts.append(part + markdown_string.rstrip() + '\n')

    body = '\n---\n\n'.join(parts)
    if options['title']:
        body = '# ' + options['title'] + '\n\n' + body

    response = app.response_class(body, mimetype='text/markdown')
    response.headers['Content-Disposition'] = (
        'attachment; filename="' +
        get_download_filename(options['title'], '.md') + '"')
    return response
