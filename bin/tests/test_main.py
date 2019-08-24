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
import json
import tempfile
from urllib.error import URLError
from unittest.mock import patch
from unittest.mock import MagicMock

sys.path.append('.')
target = __import__("vallenato_fr")
aprender = __import__("aprender")
website = __import__("website")

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

    def test_parse_args_dump_uploaded_videos_aprender(self):
        """
        Test running the script with invalid arguments combination:
        --dump-uploaded-videos with --aprender instead of --website
        """
        with self.assertRaises(SystemExit) as cm:
            parser = target.parse_args(['--dump-uploaded-videos', '--aprender'])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 18)


class TestInitMain(unittest.TestCase):
    @patch("aprender.get_title_author_tutocreator_and_channel")
    @patch("aprender.YouTube")
    @patch("webbrowser.open")
    def test_aprender(self, mockwbopen, a_yt, a_gtatac):
        """
        Test the initialization code with only the --aprender parameter
        """
        # Make the script believe we ran it directly
        target.__name__ = "__main__"
        # Pass it just the --aprender argument
        target.sys.argv = ["scriptname.py", "--aprender"]
        # Pass it two valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
            "blabla-bla"
        ]
        # Define the expected return value for aprender.get_title_author_tutocreator_and_channel
        # This prevents lengthy network operations
        yt_tutorial_video = MagicMock()
        a_gtatac.return_value = ("Bonita cancion", "Super cantante", "El Vallenatero Francés", "UC_8R235jg1ld6MCMOzz2khQ", yt_tutorial_video)
        # Create a copy of the index.html file that is going to be edited
        shutil.copy("../aprender/index.html", "../aprender/index.html.bak")
        # Run the init(), will run the full --aprender branch
        target.init()
        # Confirm that a new tutorial page has been created in the temporary folder
        self.assertTrue(os.path.exists("../aprender/blabla-bla.html"))
        # Confirm that the content of the new template has been updated
        with open("../aprender/blabla-bla.html", 'r') as file :
            filedata = file.read()
            self.assertTrue("<title>Bonita cancion - Super cantante</title>" in filedata)
            self.assertTrue('<span id="nameCurrent">Bonita cancion - Super cantante</span>' in filedata)
            self.assertTrue('{"id": "oPEirA4pXdg", "start": 0, "end": 999}' in filedata)
            self.assertTrue('var fullVersion = "q6cUzC6ESZ8";' in filedata)
        # Confirm that a temporary file with the content to be added to the index page has been created
        with open("../aprender/index.html", 'r') as file :
            filedata = file.read()
            self.assertTrue('\n      <li><a href="blabla-bla.html">Bonita cancion - Super cantante</a> - NNmNNs en NN partes</li>' in filedata)
            self.assertTrue('\n      <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>' in filedata)
        # Confirm the webbrowser is called to be opened to the new template's page
        mockwbopen.assert_called_once_with("../aprender/blabla-bla.html", autoraise=True, new=2)
        # Delete that new tutorial page
        os.remove("../aprender/blabla-bla.html")
        # Restore the index page
        os.remove("../aprender/index.html")
        shutil.move("../aprender/index.html.bak", "../aprender/index.html")

    @patch("website.get_uploaded_videos")
    def test_website(self, w_guv):
        # Make the script believe we ran it directly
        target.__name__ = "__main__"
        # Pass it just the --aprender argument
        target.sys.argv = ["scriptname.py", "--website"]
        # Mock valid list of videos
        with open("tests/data/sample_uploaded_videos_dump_partial.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        w_guv.return_value = sample_uploaded_videos
        # Redirect the output to a temporary file
        (ignore, temp_file) = tempfile.mkstemp()
        website.WEBSITE_DATA_FILE = temp_file
        # Run the init(), will run the full --website branch
        target.init()
        #TODO Assert final script result
        # Delete the temporary file created by the test
        os.remove(temp_file)


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
