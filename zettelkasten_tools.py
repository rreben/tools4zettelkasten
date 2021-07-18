#!/usr/bin/env python

# zettelkasten.py

# Copyright (c) 2021 Rupert Rebentisch
# Licensed under the MIT license

import markdown
from flask import Flask, \
    render_template, \
    send_from_directory, \
    request
# pygments does some magic on the import
# therefore we able the pylint for this line of code
from pygments.formatters import HtmlFormatter
# pylint: disable=no-name-in-module
import re
import os
import logging
# from datetime import datetime
import argparse
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from flask_pagedown import PageDown
from pprint import pprint
from pyfiglet import Figlet
from InquirerPy import prompt
from zettelkasten_tools import settings, handle_filenames


class ZettelkastenTools:

    @staticmethod
    def run():
        print('hello world')


class PageDownFormExample(Form):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Submit')


app = Flask(__name__, template_folder=settings.TEMPLATE_FOLDER,
            static_folder=settings.STATIC_FOLDER)
pagedown = PageDown(app)
input_directory = settings.ZETTELKASTEN_INPUT
zettelkasten_directory = settings.ZETTELKASTEN







def generate_list_of_zettelkasten_files():
    zettelkasten_list = []
    if os.path.exists(zettelkasten_directory):
        for filename in os.listdir(zettelkasten_directory):
            if ('md' == os.path.splitext(filename)[1][1:].strip().lower()):
                zettelkasten_list.append(filename)
    else:
        logging.error("zettelkasten directrory not found")
    return zettelkasten_list



@app.route('/<file>')
def show_md_file(file):
    filename = file
    input_file = open(zettelkasten_directory + '/' + file, "r")
    htmlString = markdown.markdown(
        input_file.read(), output_format='html5',
        extensions=[
            "fenced_code",
            'codehilite',
            'attr_list',
            'pymdownx.arithmatex'],
        extension_configs={'pymdownx.arithmatex': {'generic': True}}
    )
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()

    # return md_css_string + htmlString
    return render_template(
        "mainpage.html",
        codeCSSString="<style>" + css_string + "</style>",
        htmlString=htmlString,
        filename=filename)


@app.route('/')
def start():
    zettelkasten_list = generate_list_of_zettelkasten_files()
    # print(zettelkasten_list)
    zettelkasten_list.sort()
    # print(zettelkasten_list)
    return render_template('startpage.html', zettelkasten=zettelkasten_list)


def write_markdown_to_file(filename, markdown_string):
    if os.path.exists(zettelkasten_directory):
        with open(
                zettelkasten_directory + '/' + filename, 'w') as markdown_file:
            markdown_file.write(markdown_string)
    else:
        logging.error("zettelkasten_directory does not exist")


@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit(filename):
    input_file = open(zettelkasten_directory + '/' + filename, "r")
    markdown_string = input_file.read()
    form = PageDownFormExample()
    form.pagedown.data = markdown_string
    if form.validate_on_submit():
        if request.method == 'POST':
            new_markdown_string = request.form['pagedown']
            form.pagedown.data = new_markdown_string
            write_markdown_to_file(filename, new_markdown_string)
    return render_template('edit.html', form=form)


@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory(app.config["MYCELIUM_IMAGES"], filename)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # We use arparse to specify the CLI
    # Description is the program description in the help message
    parser = argparse.ArgumentParser(
        description=(
            "A set of tools for a simple Zettelkasten,"
            "no arguments start flask"))
    # action="store_true" makes -b --batchimport
    # to a flag so no further arguments are expected
    # the flag is true when specified in the commandline otherwise false
    parser.add_argument(
        '-b', '--batchimport',
        help='process all files in the input directory',
        action="store_true")
    parser.add_argument('-r', '--reorganize',
                        help='rename files to reorganize directory',
                        action="store_true")
    parser.add_argument('-i', '--attach_ids',
                        help='attach missing IDs to files',
                        action="store_true")
    args = parser.parse_args()

    f = Figlet(font='slant')
    print(f.renderText('zettelkasten tools'))
    if args.batchimport:
        process_files_from_input()
    elif args.reorganize:
        reorganize_mycelium()
    elif args.attach_ids:
        attach_missing_ids()
    else:
        SECRET_KEY = os.urandom(32)
        app.config['SECRET_KEY'] = SECRET_KEY
        app.debug = True
        app.config["MYCELIUM_IMAGES"] = (
            "/Users/rupertrebentisch/Dropbox/zettelkasten/mycelium/images")
        app.run()
