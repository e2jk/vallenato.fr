#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && rm -rf ../html_dev/coverage && coverage html --directory=../html_dev/coverage --title="Code test coverage for vallenato.fr"

import unittest
import sys
import os
import shutil
import logging
import socket
from urllib.error import URLError
from unittest.mock import patch

sys.path.append('.')
target = __import__("vallenato_fr")
aprender = __import__("aprender")

# Check if we're connected to the Internet
def is_connected():
    try:
        # See if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname("duckduckgo.com")
        # Connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except socket.gaierror:
        pass
    return False

# Used to test manual entry
def setUpModule():
    def mock_raw_input(s):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter += 1
        return mock_raw_input_values[mock_raw_input_counter - 1]
    aprender.input = mock_raw_input


class TestParseArgs(unittest.TestCase):
    def test_parse_args_no_arguments(self):
        """
        Test running the script without one of the required arguments --aprender or --website
        """
        with self.assertRaises(SystemExit) as cm:
            parser = target.parse_args([])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 2)

    def test_parse_args_aprender_website(self):
        """
        Test running the script without both mutually exclusive arguments --aprender and --website
        """
        with self.assertRaises(SystemExit) as cm:
            parser = target.parse_args(['--aprender', '--website'])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 2)

    def test_parse_args_no_download(self):
        """
        Test the --no-download argument
        """
        parser = target.parse_args(['--no-download', '--aprender'])
        self.assertTrue(parser.no_download)

    def test_parse_args_no_download_shorthand(self):
        """
        Test the -nd argument
        """
        parser = target.parse_args(['-nd', '--aprender'])
        self.assertTrue(parser.no_download)

    def test_parse_args_debug(self):
        """
        Test the --debug argument
        """
        parser = target.parse_args(['--debug', '--aprender'])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")

    def test_parse_args_debug_shorthand(self):
        """
        Test the -d argument
        """
        parser = target.parse_args(['-d', '--aprender'])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")

    def test_parse_args_verbose(self):
        """
        Test the --verbose argument
        """
        parser = target.parse_args(['--verbose', '--aprender'])
        self.assertEqual(parser.loglevel, logging.INFO)
        self.assertEqual(parser.logging_level, "INFO")

    def test_parse_args_verbose_shorthand(self):
        """
        Test the -v argument
        """
        parser = target.parse_args(['-v', '--aprender'])
        self.assertEqual(parser.loglevel, logging.INFO)
        self.assertEqual(parser.logging_level, "INFO")

    def test_parse_args_temp_folder_website(self):
        """
        Test running the script with invalid arguments combination:
        --temp-folder with --website instead of --aprender
        """
        with self.assertRaises(SystemExit) as cm:
            parser = target.parse_args(['--temp-folder', '--website'])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 16)

    def test_parse_args_no_download_website(self):
        """
        Test running the script with invalid arguments combination:
        --no-download with --website instead of --aprender
        """
        with self.assertRaises(SystemExit) as cm:
            parser = target.parse_args(['--no-download', '--website'])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 17)


class TestInitMain(unittest.TestCase):
    # def test_init_main_no_arguments(self):
    #     """
    #     Test the initialization code without any parameter
    #     """
    #     # Make the script believe we ran it directly
    #     target.__name__ = "__main__"
    #     # Pass it no arguments
    #     target.sys.argv = ["scriptname.py"]
    #     # Pass it two valid YouTube URLs
    #     global mock_raw_input_counter
    #     global mock_raw_input_values
    #     mock_raw_input_counter = 0
    #     mock_raw_input_values = [
    #         "http://www.youtube.com/watch?v=oPEirA4pXdg",
    #         "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
    #         "Bonita cancion",
    #         "Super cantante",
    #         "blabla-bla"
    #     ]
    #     # Create a copy of the index.html file that is going to be edited
    #     shutil.copy("../aprender/index.html", "../aprender/index.html.bak")
    #     # Run the init(), the program exits correctly
    #     target.init()
    #     # Confirm that a new tutorial page has been created
    #     self.assertTrue(os.path.exists("../aprender/blabla-bla.html"))
    #     # Confirm that the content of the new template has been updated
    #     with open("../aprender/blabla-bla.html", 'r') as file :
    #         filedata = file.read()
    #     self.assertTrue("<title>Bonita cancion</title>" in filedata)
    #     self.assertTrue('<span id="nameCurrent">Bonita cancion</span>' in filedata)
    #     self.assertTrue('{"id": "oPEirA4pXdg", "start": 0, "end": 999}' in filedata)
    #     self.assertTrue('var fullVersion = "q6cUzC6ESZ8";' in filedata)
    #     # Confirm that the index page has been updated
    #     with open("../aprender/index.html", 'r') as file :
    #         filedata = file.read()
    #     self.assertTrue('</li>\n      <li><a href="blabla-bla.html">Bonita cancion - Super cantante</a> - NNmNNs en NN partes</li>\n    </ul>' in filedata)
    #     self.assertTrue('</a></li>\n      <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>\n    </ul>' in filedata)
    #     # Delete that new tutorial page
    #     os.remove("../aprender/blabla-bla.html")
    #     # Restore the index page
    #     os.remove("../aprender/index.html")
    #     shutil.move("../aprender/index.html.bak", "../aprender/index.html")

    @patch("aprender.get_title_author_tutocreator_and_channel")
    @patch("webbrowser.open")
    def test_init_main_aprender_temp_folder_no_download(self, mockwbopen, a_gtatac):
        """
        Test the initialization code with the --temp-folder and --no-download parameters
        """
        # Make the script believe we ran it directly
        target.__name__ = "__main__"
        # Pass it no arguments
        target.sys.argv = ["scriptname.py", "--aprender", "--debug", "--temp-folder", "--no-download"]
        # Pass it two valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
            "blabla-bla"
        ]
        # Run the init(), the program exits correctly
        if is_connected():
            # Define the expected return value for aprender.get_title_author_tutocreator_and_channel
            # This prevents lengthy network operations
            a_gtatac.return_value = ("Bonita cancion", "Super cantante", "El Vallenatero Francés", "UC_8R235jg1ld6MCMOzz2khQ", None)
            target.init()
            # Confirm that a new tutorial page has been created in the temporary folder
            self.assertTrue(os.path.exists("../aprender/temp/blabla-bla/blabla-bla.html"))
            # Confirm that the content of the new template has been updated
            with open("../aprender/temp/blabla-bla/blabla-bla.html", 'r') as file :
                filedata = file.read()
                self.assertTrue("<title>Bonita cancion - Super cantante</title>" in filedata)
                self.assertTrue('<span id="nameCurrent">Bonita cancion - Super cantante</span>' in filedata)
                self.assertTrue('{"id": "oPEirA4pXdg", "start": 0, "end": 999}' in filedata)
                self.assertTrue('var fullVersion = "q6cUzC6ESZ8";' in filedata)
            # Confirm that a temporary file with the content to be added to the index page has been created
            with open("../aprender/temp/blabla-bla/index-dummy.html", 'r') as file :
                filedata = file.read()
                self.assertTrue('\n      <li><a href="blabla-bla.html">Bonita cancion - Super cantante</a> - NNmNNs en NN partes</li>' in filedata)
                self.assertTrue('\n      <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>' in filedata)
                # Delete the temporary folder
                shutil.rmtree("../aprender/temp/blabla-bla/")
            # Confirm the webbrowser is called to be opened to the new template's page
            mockwbopen.assert_called_once_with("../aprender/temp/blabla-bla/blabla-bla.html", autoraise=True, new=2)
        else:
            with self.assertRaises(URLError) as cm:
                target.init()
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """Validate that the project has a LICENSE file, check part of its content"""
        self.assertTrue(os.path.isfile("LICENSE"))
        with open('LICENSE') as f:
            s = f.read()
            # Confirm it is the GNU Affero General Public License version 3
            self.assertTrue("GNU AFFERO GENERAL PUBLIC LICENSE\n                       Version 3" in s)

    def test_license_mention(self):
        """Validate that the script file contain a mention of the license"""
        with open('vallenato_fr.py') as f:
            s = f.read()
            # Confirm it is the GNU Affero General Public License version 3
            self.assertTrue(
                "#    This file is part of Vallenato.fr.\n"
                "#\n"
                "#    Vallenato.fr is free software: you can redistribute it and/or modify\n"
                "#    it under the terms of the GNU Affero General Public License as published by\n"
                "#    the Free Software Foundation, either version 3 of the License, or\n"
                "#    (at your option) any later version.\n"
                in s)


if __name__ == '__main__':
    unittest.main()