# flask_views.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

from ast import Str
from flask import (
    Flask, render_template, send_from_directory, redirect, url_for, request,
    session, jsonify)
from . import settings as st
from . import analyse as an
from . import reorganize as ro
from .persistency import PersistencyManager
import markdown
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


class PageDownForm(FlaskForm):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Save')


def run_flask_server():
    """Run the flask server on port 5001.

    Port 5001 is used instead of the Flask default 5000
    because macOS Monterey and later use port 5000 for AirPlay Receiver.
    """
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
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


@app.route('/')
def index():
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    zettelkasten_list = get_sorted_zettelkasten_list(persistencyManager)
    return render_template('startpage.html', zettelkasten=zettelkasten_list)


@app.route('/<file>')
def show_md_file(file):
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    filename = file

    # Hierarchisch sortierte Liste für Navigation ermitteln
    sorted_list = get_sorted_zettelkasten_list(persistencyManager)
    previous_file, next_file = get_adjacent_files(filename, sorted_list)

    input_file = persistencyManager.get_string_from_file_content(filename)
    htmlString = markdown.markdown(
        input_file, output_format='html5',
        extensions=[
            "fenced_code",
            'codehilite',
            'attr_list',
            'pymdownx.arithmatex'],
        extension_configs={'pymdownx.arithmatex': {'generic': True}}
    )
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()
    return render_template(
        "mainpage.html",
        codeCSSString="<style>" + css_string + "</style>",
        htmlString=htmlString,
        filename=filename,
        previous_file=previous_file,
        next_file=next_file)


@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit(filename):
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
    return send_from_directory(
        st.ZETTELKASTEN_IMAGES,
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
