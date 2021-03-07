# We first create the search path for the modules
# so that zettelkasten kan be found
# Start tests with python test/test_zettelkasten.py
# from the parent directory

import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import unittest
import re
import logging
import zettelkasten

class TestCanonizeFilename(unittest.TestCase):

    def test_trailing_spaces(self):
        self.assertEqual(zettelkasten.canonize_filename('foo  '), 'foo')

    def test_multiple_spaces_removed(self):
        self.assertEqual(zettelkasten.canonize_filename('foo   bar'), 'foo_bar')

    def test_replace_spaces_with_underscores(self):
        self.assertEqual(zettelkasten.canonize_filename('How to connect a local flask server to the internet'), 'How_to_connect_a_local_flask_server_to_the_internet')

    def test_replace_umlaute(self):
        self.assertEqual(zettelkasten.canonize_filename('Testen ist nicht öde oder ärgerlich'), 'Testen_ist_nicht_oede_oder_aergerlich')

    def test_remove_special_characters(self):
        self.assertEqual(zettelkasten.canonize_filename('Testen ist nicht öde! oder ärgerlich?'), 'Testen_ist_nicht_oede_oder_aergerlich')

class TestGetId(unittest.TestCase):
    def test_hash(self):
        self.assertEqual(zettelkasten.evaluate_sha_256('foo  '), '07e67ea4439b8f4513d4140fe54229ac127fe0b39ef740136892c433d311a41a')

    def test_currentTimestamp(self):
        assert re.match('^[0-9]{1,14}$', zettelkasten.currentTimestamp())

class TestProcessInput(unittest.TestCase):
    def test_process_files_from_input(self):
        # zettelkasten.process_files_from_input()
        self.assertEqual(zettelkasten.evaluate_sha_256('foo  '), '07e67ea4439b8f4513d4140fe54229ac127fe0b39ef740136892c433d311a41a')



if __name__ == '__main__':
    logging.basicConfig(filename='testsuite.log', level=logging.INFO)
    unittest.main()
