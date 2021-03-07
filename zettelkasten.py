import markdown
from flask import Flask, render_template
from pygments.formatters import HtmlFormatter
import re
import os
import logging
from datetime import datetime
import argparse


app = Flask(__name__)
input_directory = '../zettelkasten/input'
zettelkasten_directory = '../zettelkasten/mycellium'
startscreen = """#Zettelkasten
These are the topics you are **probing**:
"""

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
            print('process file: ' + filename)
            # do not process hidden files
            if not (filename[0] == '.'):
                # txt-file?
                if ('txt' == os.path.splitext(filename)[1][1:].strip().lower()):
                    print(process_txt_file(input_directory + '/' + filename))
    else:
        logging.error("input directrory not found")

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

def evaluate_sha_256(input):
    import hashlib
    input = input.encode('utf-8')
    hash_object = hashlib.sha256(input)
    hex_dig = hash_object.hexdigest()
    return(hex_dig)

def currentTimestamp():
    now = datetime.now()
    return  now.strftime("%Y%m%d%H%M%S")


@app.route('/<file>')
def show_md_file(file):
    input_file = open(file, "r")
    htmlString = markdown.markdown(
        input_file.read(), output_format='html5',
        extensions=["fenced_code",'codehilite','attr_list', 'pymdownx.arithmatex'],
        extension_configs = {'pymdownx.arithmatex':{'generic':True}}
    )
    formatter = HtmlFormatter(style="emacs",full=True,cssclass="codehilite")
    css_string = formatter.get_style_defs()

    # return md_css_string + htmlString
    return render_template("mainpage.html", codeCSSString = "<style>" + css_string + "</style>", htmlString = htmlString)

@app.route('/')
def start():
    htmlString = markdown.markdown(startscreen)
    return htmlString

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # We use arparse to specify the CLI
    # Description is the program description in the help message
    parser = argparse.ArgumentParser(description="A set of tools for a simple Zettelkasten, no arguments start flask")
    # action="store_true" makes -b --batchimport to a flag so no further arguments are expected
    # the flag is true when specified in the commandline otherwise false
    parser.add_argument('-b','--batchimport', help='process all files in the input directory', action="store_true")
    args = parser.parse_args()
    if args.batchimport:
        process_files_from_input()
    else:
        app.debug = True
        app.run()
