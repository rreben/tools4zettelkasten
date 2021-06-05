# handle_filenames.py

import re
import hashlib
from datetime import datetime


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
    if re.match(r'.*_[0-9a-f]{9}\.md$', filename):
        id_filename = filename[-12:-3]
        filename = filename[:-13]
    # Split by first underscore followed by a character = Non-Digit
    ordering_filename = re.split(r'_\D', filename, maxsplit=1)[0]
    base_filename = filename[(len(ordering_filename)+1):]
    components = [ordering_filename, base_filename, id_filename]
    return components


def generate_id(filename):
    return evaluate_sha_256(filename + currentTimestamp())[:9]


def evaluate_sha_256(input):
    input = input.encode('utf-8')
    hash_object = hashlib.sha256(input)
    hex_dig = hash_object.hexdigest()
    return(hex_dig)


def currentTimestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S%f")
