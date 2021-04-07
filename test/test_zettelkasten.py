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
# import works pretty fine due to above setting of the src path
# But pylint isn't able to follow this, thus we have to disable it
# to prevent false pylint problems
import zettelkasten # pylint: disable=import-error
from pprint import pprint

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

class TestZettelTreeActions(unittest.TestCase):
    def test_generate_tokenized_list(self):
        zettelkasten_list = ['5_10_Senescent_cells.md', 
            '1_2_reframe_your_goal_as_a_learning_goal.md', 
            '2_1a_render_md_files_with_python_and_flask.md', 
            '2_5_homebrew.md', 
            '2_4_create_a_ssl_certificate.md', 
            '2_4_1_sometest.md',
            '5_2_Gedanken_zum_Survival_Mechanism.md', 
            '5_4_Die_Rolle_des_Epigenoms.md', 
            '1_1a_Mein_Zettelkasten_Workflow.md', 
            '2_1c_Editing_markdown_files_via_flask.md', 
            '2_1b_Show_images_in_Flask_generated_HTML_Files_from_markdown.md', 
            '3_5_Angst_vor_der_Wahrheit_nach_dem_Release.md', 
            '1_3_Keep_it_Low_Tech.md', 
            '5_8_Die_Marathon_Mouse.md', 
            '3_4_Erfolgsfaktor_Datenschutz.md', 
            '5_1_Primordial_Survival_Mechanism.md', 
            '5_9_The_Gompertz_Equation.md', 
            '5_7_Die_Ice_Mouse.md', 
            '5_7_1_Some_More_Information_on_Ice_Mouse.md',
            '5_7_2_Even_More_Information_on_Ice_Mose.md',
            '4_1_Gestaltung_des_Building_Block_neue_Technologien.md', 
            '2_1_Combine_Flask_and_Markdown.md', 
            '5_12_Medikamente_fuer_ein_laengeres_Leben.md', 
            '2_6_Inner_workings_of_Git.md', 
            '1_1_Claim.md', 
            '5_3_The_Hallmarks_of_Aging.md', 
            '3_1_Cloud_Einsatzgebiete_bei_der_KfW.md', 
            '1_3b_Kanonisch.md', 
            '3_7_Warum_kriegt_YGGS_nun_mehr_Fokus_als_der_FöA_Ohne_Schubumkehr_kein_Traffic.md', 
            '1_4_Pruning.md', 
            '5_5a_Die_Waddington_Map.md', 
            '5_6_Untersuchungen_an_Hefezellen.md', 
            '1_0_Mycelium_of_Knowledge.md', 
            '3_6_Warum_die_Schubumkehr_nicht_funktioniert.md', 
            '5_6a_Longevity_genes_in_roundworms.md', 
            '3_1a_Risikoueberlegungen_fuer_Cloud_Einsatzgebiete.md', 
            '4_2_Von_den_Ressourcen_her_denken.md', 
            '3_2a_Hybridloesungen.md', 
            '2_3_virtualenv.md', 
            '5_5_Die_Rolle_der_Sirtuins.md', 
            '3_3_Kann_byok_customer_lockbox_ersetzen.md', 
            '2_2_how_to_connect_a_local_flask_server_to_the_internet.md', 
            '1_1b_Open_mind_for_using_the_Zettelkasten.md', 
            '5_11_Age_reversal.md', 
            '3_2_Datenökosysteme_als_neues_Cloudeinsatzgebiet_und_neue_Klasse_von_Anwendungen.md', 
            '1_3a_Importance_of_Software_for_the_Zettelkasten_method.md', 
            '3_4a_Cloud_Strategie_muss_der_Geschaeftsstrategie_folgen.md', 
            '5_13_Advice_for_a_longer_living.md']
        tree=zettelkasten.generate_tree(zettelkasten.generate_tokenized_list(zettelkasten_list))
        pprint(tree)
        #pprint(tree[4][1:])
        #tree=zettelkasten.generate_tree(tree[4][1:])
        self.assertEqual(zettelkasten.generate_tokenized_list(zettelkasten_list)[0][0][0],'5')


if __name__ == '__main__':
    logging.basicConfig(filename='testsuite.log', level=logging.INFO)
    unittest.main()
