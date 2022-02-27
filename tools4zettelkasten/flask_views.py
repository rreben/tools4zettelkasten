# flask_views.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license

from ast import Str
from flask import (
    Flask, render_template, send_from_directory, redirect, url_for, request)
from . import settings as st
from . import analyse as an
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
    submit = SubmitField('Submit')


def run_flask_server():
    """Run the flask server"""
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.debug = True
    app.run()


def url_for_file(filename) -> Str:
    URL = url_for('show_md_file', file=filename)
    return URL


@app.route('/')
def index():
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    zettelkasten_list = persistencyManager.get_list_of_filenames()
    zettelkasten_list.sort()
    return render_template('startpage.html', zettelkasten=zettelkasten_list)


@app.route('/<file>')
def show_md_file(file):
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    filename = file
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
        filename=filename)


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
    return render_template('edit.html', form=form)


@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory(
        st.ABSOLUTE_PATH_IMAGES,
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
