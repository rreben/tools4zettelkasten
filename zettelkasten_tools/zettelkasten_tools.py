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
from datetime import datetime
import argparse
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from flask_pagedown import PageDown
from pprint import pprint
from pyfiglet import Figlet
from InquirerPy import prompt


class PageDownFormExample(Form):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Submit')


app = Flask(__name__, template_folder='../flask_frontend/templates',
            static_folder='../flask_frontend/static')
pagedown = PageDown(app)
input_directory = '../zettelkasten/input'
zettelkasten_directory = '../zettelkasten/mycelium'


def process_txt_file(pathname):
    filename = 'Error'
    with open(pathname, 'r') as afile:
        content = afile.readlines()
        if (content[0][0] == '#'):
            filename = content[0][2:]
            filename = canonize_filename(filename)
        os.rename(pathname, input_directory + '/' + filename + '.md')


def process_files_from_input():
    if os.path.exists(input_directory):
        for filename in os.listdir(input_directory):
            # do not process hidden files
            if not (filename[0] == '.'):
                # txt-file?
                if ('txt' == os.path.splitext(filename)[1][1:].strip().lower()
                    or
                    'md' == os.path.splitext(filename)[1][1:].strip().lower()):
                    print(process_txt_file(input_directory + '/' + filename))
    else:
        logging.error("input directrory not found")


def reorganize_filenames(tree, path=None, final=None):
    if final is None:
        final = []
    if path is None:
        path = ''
    for node in tree:
        if isinstance(node, list):
            if len(node) == 2:
                if isinstance(node[0], str) and isinstance(node[1], str): 
                    final.append(
                        [path + node[0], node[1]])
                else:
                    reorganize_filenames(node, path=path, final=final)
            else:
                if len(node) == 3:
                    if isinstance(node[0], str) and isinstance(node[1], str) and isinstance(node[2], list):
                        final.append([path + node[0], node[1]])
                        reorganize_filenames(
                            node[2], path=path + node[0] + '_', final=final)
                else:
                    reorganize_filenames(node, path=path, final=final)
        else:
            path += node + '_'
    return final


def corrections_elements(list_of_keys):
    list_of_keys_with_leading_zeros = []
    corrections_elements_dict = {}
    number_of_necessary_digits = len(str(abs(len(list_of_keys))))
    for i in range(len(list_of_keys)):
        number_of_digits = sum(c.isdigit() for c in list_of_keys[i])
        leading_zeros = '0' * (number_of_necessary_digits - number_of_digits)
        list_of_keys_with_leading_zeros.append([list_of_keys[i], leading_zeros + list_of_keys[i]])
    list_of_keys_with_leading_zeros.sort(key=lambda x: x[1])
    for i in range(len(list_of_keys_with_leading_zeros)):
        j = i + 1
        number_of_digits = sum(c.isdigit() for c in str(j))
        leading_zeros = '0' * (number_of_necessary_digits - number_of_digits)
        list_of_keys_with_leading_zeros[i].append(leading_zeros + str(j))
        corrections_elements_dict[list_of_keys_with_leading_zeros[i][0]] = list_of_keys_with_leading_zeros[i][2]
    return corrections_elements_dict


def generate_tree(tokenized_list):
    tree_keys = [x[0][0] for x in tokenized_list]
    tree_keys.sort()
    # remove duplicates
    tree_keys = list(dict.fromkeys(tree_keys))
    corrections_elements_dict = corrections_elements(tree_keys)
    tree =[]
    for tree_key in tree_keys:
        sub_tree = []
        sub_tokenized_list = []
        sub_tree.append(corrections_elements_dict[tree_key])
        for x in tokenized_list:
            if x[0][0] == tree_key:
                if len(x[0]) == 1:
                    sub_tree.append(x[1])
                else:
                    sub_tokenized_list.append([x[0][1:],x[1]])
                    # sub_tree.append(generate_tree([x[0][1:],x[1]]))
        #sub_tree.append([[x[0][1:], x[1]] for x in tokenized_list if x[0][0] == tree_key])
        if len(sub_tokenized_list) >0:
            sub_tree.append(generate_tree(sub_tokenized_list))
        tree.append(sub_tree)
    tree.sort(key=lambda x: x[0])
    return tree


def generate_tokenized_list(zettelkasten_list):
    tokenized_list = []
    for filename in zettelkasten_list:
        filename_components = re.split(r'_\D', filename, maxsplit=1)
        numbering_in_filename_and_filename = [re.split(r'_', filename_components[0]), filename]
        #if match:
        #    trunk_filen_name = match.group()
        tokenized_list.append(numbering_in_filename_and_filename)
    return tokenized_list


def generate_list_of_zettelkasten_files():
    zettelkasten_list = []
    if os.path.exists(zettelkasten_directory):
        for filename in os.listdir(zettelkasten_directory):
            if ('md' == os.path.splitext(filename)[1][1:].strip().lower()):
                zettelkasten_list.append(filename)
    else:
        logging.error("zettelkasten directrory not found")
    return zettelkasten_list


def canonize_filename(filename):
    # filename extension is md
    # remove leading and trailing whitespaces
    filename = filename.strip()
    # remove multiple whitespaces
    filename = " ".join(filename.split())
    # replace all öäüß with oe, ae, ue, ss
    filename = filename.replace("ä", "ae")
    filename = filename.replace("ö", "oe")
    filename = filename.replace("ü", "ue")
    filename = filename.replace("Ä", "Ae")
    filename = filename.replace("Ö", "Oe")
    filename = filename.replace("Ü", "Ue")
    filename = filename.replace("ß", "ss")
    # replace all spaces with underscore
    filename = filename.replace(" ", "_")
    # remove special characters like ?
    filename = re.sub('[^A-Za-z0-9_]+', '', filename)
    return filename


def get_filename_components(filename):
    components = []
    id_filename = ''
    if re.match('.*_[0-9a-f]{9}\.md$', filename):
        id_filename = filename[-12:-3]
        filename = filename[:-13]
    # Split by first underscore followed by a character = Non-Digit
    ordering_filename = re.split(r'_\D', filename, maxsplit=1)[0]
    base_filename = filename[(len(ordering_filename)+1):]
    components = [ordering_filename, base_filename, id_filename]
    return components


def generate_id(filename):
    return evaluate_sha_256(filename + currentTimestamp())[:9]


def attach_missing_ids():
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": False,
        }
    ]
    for filename in generate_list_of_zettelkasten_files():
        components = get_filename_components(filename)
        file_id = generate_id(filename)
        if components[2] == '':
            oldfilename = filename
            newfilename = components[0] + '_' + components[1][:-3] + \
                '_' + file_id + '.md'
            print('Rename ', oldfilename, ' --> ')
            print(newfilename, '?')
            result = prompt(questions)
            if result["proceed"]:          
                rename_file(oldfilename, newfilename)


def rename_file(oldfilename, newfilename):
    if os.path.exists(zettelkasten_directory):
        oldfile = zettelkasten_directory + '/' + oldfilename
        newfile = zettelkasten_directory + '/' + newfilename
        os.rename(oldfile, newfile)
        print('renamed: ', oldfile, ' with: ', newfile)
    else:
        logging.error("rename-error: zettelkasten directrory not found")


def reorganize_mycelium():
    tree = []
    tree = generate_tree(
        generate_tokenized_list(generate_list_of_zettelkasten_files()))
    # pprint(tree)
    potential_changes_of_filenames = reorganize_filenames(tree)
    changes_of_filenames = [[x[0], x[1]] for x in potential_changes_of_filenames if x[0] != re.split(r'_\D', x[1], maxsplit=1)[0]]
    print()
    print('The following changes will be done:')
    pprint([x[0] + ' --> ' + x[1] for x in changes_of_filenames])
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": False,
        }
    ]
    result = prompt(questions)
    if result["proceed"]:
        if os.path.exists(zettelkasten_directory):
            for x in changes_of_filenames:
                oldfile = zettelkasten_directory + '/' + x[1]
                newfile = zettelkasten_directory + '/' + x[0] + '_' + get_filename_components(x[1])[1]
                os.rename(oldfile, newfile)
                print('renamed: ', oldfile, ' with: ', newfile)
        else:
            logging.error("reorg-error: zettelkasten directrory not found")


def evaluate_sha_256(input):
    import hashlib
    input = input.encode('utf-8')
    hash_object = hashlib.sha256(input)
    hex_dig = hash_object.hexdigest()
    return(hex_dig)


def currentTimestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S%f")


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
        with open(zettelkasten_directory + '/' + filename, 'w') as markdown_file:
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
    parser = argparse.ArgumentParser(description="A set of tools for a simple Zettelkasten, no arguments start flask")
    # action="store_true" makes -b --batchimport to a flag so no further arguments are expected
    # the flag is true when specified in the commandline otherwise false
    parser.add_argument(
        '-b', '--batchimport',
        help='process all files in the input directory',
        action="store_true")
    parser.add_argument('-r', '--reorganize',
                        help='rename files to reorganize directory', action="store_true")
    parser.add_argument('-i', '--attach_ids',
                        help='attach missing IDs to files', action="store_true")
    args = parser.parse_args()
    
    f = Figlet(font='slant')
    print (f.renderText('zettelkasten tools'))
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
        app.config["MYCELIUM_IMAGES"] = "/Users/rupertrebentisch/Dropbox/zettelkasten/mycelium/images"
        app.run()