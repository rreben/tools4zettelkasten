# test_handle_filenames.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from .context import tools4zettelkasten as zt
import re


def test_trailing_spaces():
    assert zt.handle_filenames.create_base_filename_from_title(
        'foo  ') == 'foo'


def test_multiple_spaces_removed():
    assert zt.handle_filenames.create_base_filename_from_title(
        'foo   bar') == 'foo_bar'


def test_replace_spaces_with_underscores():
    assert (zt.handle_filenames.create_base_filename_from_title(
        'How to connect a local flask server to the internet')
        ==
        'How_to_connect_a_local_flask_server_to_the_internet')


def test_replace_umlaute():
    assert (zt.handle_filenames.create_base_filename_from_title(
        'Testen ist nicht öde oder ärgerlich')
        ==
        'Testen_ist_nicht_oede_oder_aergerlich')


def test_remove_special_characters():
    assert (zt.handle_filenames.create_base_filename_from_title(
        'Testen ist nicht öde! oder ärgerlich?')
        ==
        'Testen_ist_nicht_oede_oder_aergerlich')


def test_hash():
    assert (zt.handle_filenames.evaluate_sha_256(
        'foo  ')
        ==
        '07e67ea4439b8f4513d4140fe54229ac127fe0b39ef740136892c433d311a41a')


def test_currentTimestamp():
    assert re.match(
        '^[0-9]{1,20}$', zt.handle_filenames.currentTimestamp())
