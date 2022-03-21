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


def test_get_filename_components():
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[0]
        == '01_36')
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[1]
        == 'Beispiel_fuer_eine_Core_Conflict_Cloud_CCC')
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[2]
        == '6f4175c6f')
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[0]
        == '01_36')
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[1]
        == 'Beispiel_fuer_eine_Core_Conflict_Cloud_CCC')
    assert (zt.handle_filenames.get_filename_components(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[2]
        == '')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[0]
        == '')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[1]
        == 'Beispiel_fuer_eine_Core_Conflict_Cloud_CCC')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")[2]
        == '')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[0]
        == '')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[1]
        == 'Beispiel_fuer_eine_Core_Conflict_Cloud_CCC')
    assert (zt.handle_filenames.get_filename_components(
        "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")[2]
        == '6f4175c6f')


def test_create_Note():
    note = zt.handle_filenames.create_Note(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")
    assert note.base_filename == "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC"
    assert note.id == "6f4175c6f"
    assert note.ordering == "01_36"


def test_is_valid_filename():
    # valid
    assert zt.handle_filenames.is_valid_filename(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")
    # invalid id to short
    assert not zt.handle_filenames.is_valid_filename(
        "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175cf.md")
    # invalid no ordering
    assert not zt.handle_filenames.is_valid_filename(
        "A_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")
    # invalid special character ü
    assert not zt.handle_filenames.is_valid_filename(
        "01_36_Beispiel_für_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")


def test_create_filename():
    assert (zt.handle_filenames.create_filename(
            "01_36", "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC", "6f4175c6f")
            == "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")
    assert (zt.handle_filenames.create_filename(
            "", "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC", "6f4175c6f")
            == "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC_6f4175c6f.md")
    assert (zt.handle_filenames.create_filename(
        "01_36", "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC", "")
        == "01_36_Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")
    assert (zt.handle_filenames.create_filename(
        "", "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC", "")
        == "Beispiel_fuer_eine_Core_Conflict_Cloud_CCC.md")
