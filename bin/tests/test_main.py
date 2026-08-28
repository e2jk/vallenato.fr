# Running the tests (with coverage): $ sh test.sh
# Running just this file:                 $ python3 -m pytest tests/test_main.py

import contextlib
import io
import json
import logging
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(".")
target = __import__("vallenato_fr")
aprender = __import__("aprender")
website = __import__("website")


# Used to test manual entry
def setUpModule():
    def mock_raw_input(s):
        global mock_raw_input_counter
        mock_raw_input_counter += 1
        return mock_raw_input_values[mock_raw_input_counter - 1]

    aprender.input = mock_raw_input


class TestParseArgs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL)

    def test_parse_args_no_arguments(self):
        """
        Test running the script without one of the required arguments --aprender or --website
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.parse_args([])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 2)
        self.assertTrue(
            "error: one of the arguments -a/--aprender -w/--website is required"
            in f.getvalue()
        )

    def test_parse_args_aprender_website(self):
        """
        Test running the script with both mutually exclusive arguments --aprender and --website
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.parse_args(["--aprender", "--website"])
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 2)
        self.assertTrue(
            "error: argument -w/--website: not allowed with argument -a/--aprender"
            in f.getvalue()
        )

    def test_parse_args_no_download(self):
        """
        Test the --no-download argument
        """
        parser = target.parse_args(["--no-download", "--aprender"])
        self.assertTrue(parser.no_download)

    def test_parse_args_no_download_shorthand(self):
        """
        Test the -nd argument
        """
        parser = target.parse_args(["-nd", "--aprender"])
        self.assertTrue(parser.no_download)

    def test_parse_args_debug(self):
        """
        Test the --debug argument
        """
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            parser = target.parse_args(["--debug", "--aprender"])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")

    def test_parse_args_debug_shorthand(self):
        """
        Test the -d argument
        """
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            parser = target.parse_args(["-d", "--aprender"])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")

    def test_parse_args_verbose(self):
        """
        Test the --verbose argument
        """
        parser = target.parse_args(["--verbose", "--aprender"])
        self.assertEqual(parser.loglevel, logging.INFO)
        self.assertEqual(parser.logging_level, "INFO")

    def test_parse_args_verbose_shorthand(self):
        """
        Test the -v argument
        """
        parser = target.parse_args(["-v", "--aprender"])
        self.assertEqual(parser.loglevel, logging.INFO)
        self.assertEqual(parser.logging_level, "INFO")

    def test_parse_args_temp_folder_website(self):
        """
        Test running the script with invalid arguments combination:
        --temp-folder with --website instead of --aprender
        """
        with (
            self.assertRaises(SystemExit) as cm1,
            self.assertLogs(level="CRITICAL") as cm2,
        ):
            target.parse_args(["--temp-folder", "--website"])
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 16)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:vallenato_fr:The --temp-folder argument can only be used in conjunction with --aprender. Exiting..."
            ],
        )

    def test_parse_args_no_download_website(self):
        """
        Test running the script with invalid arguments combination:
        --no-download with --website instead of --aprender
        """
        with (
            self.assertRaises(SystemExit) as cm1,
            self.assertLogs(level="CRITICAL") as cm2,
        ):
            target.parse_args(["--no-download", "--website"])
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 17)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:vallenato_fr:The --no-download argument can only be used in conjunction with --aprender. Exiting..."
            ],
        )

    def test_parse_args_dump_uploaded_videos_aprender(self):
        """
        Test running the script with invalid arguments combination:
        --dump-uploaded-videos with --aprender instead of --website
        """
        with (
            self.assertRaises(SystemExit) as cm1,
            self.assertLogs(level="CRITICAL") as cm2,
        ):
            target.parse_args(["--dump-uploaded-videos", "--aprender"])
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 18)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:vallenato_fr:The --dump-uploaded-videos argument can only be used in conjunction with --website. Exiting..."
            ],
        )

    def test_parse_args_no_fetch_aprender(self):
        """
        Test running the script with invalid arguments combination:
        --no-fetch with --aprender instead of --website
        """
        with (
            self.assertRaises(SystemExit) as cm1,
            self.assertLogs(level="CRITICAL") as cm2,
        ):
            target.parse_args(["--no-fetch", "--aprender"])
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 22)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:vallenato_fr:The --no-fetch argument can only be used in conjunction with --website. Exiting..."
            ],
        )

    def test_parse_args_no_fetch_and_dump_uploaded_videos(self):
        """
        Test running the script with invalid arguments combination:
        --no-fetch together with --dump-uploaded-videos
        """
        with (
            self.assertRaises(SystemExit) as cm1,
            self.assertLogs(level="CRITICAL") as cm2,
        ):
            target.parse_args(["--no-fetch", "--dump-uploaded-videos", "--website"])
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 23)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:vallenato_fr:The --no-fetch and --dump-uploaded-videos arguments cannot be used together. Exiting..."
            ],
        )


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
            "blabla-bla",
        ]
        # Define the expected return value for aprender.get_title_author_tutocreator_and_channel
        # This prevents lengthy network operations
        yt_tutorial_video = MagicMock()
        a_gtatac.return_value = (
            "Bonita cancion",
            "Super cantante",
            "El Vallenatero Francés",
            "UC_8R235jg1ld6MCMOzz2khQ",
            yt_tutorial_video,
        )
        # Create a copy of the index.html and tutoriales data files that are going to be edited
        shutil.copy(
            "../website/src/aprender/index.html",
            "../website/src/aprender/index.html.bak",
        )
        shutil.copy(
            aprender.TUTORIALES_DATA_FILE, f"{aprender.TUTORIALES_DATA_FILE}.bak"
        )
        # Run the init(), will run the full --aprender branch
        target.init()
        # Confirm that the info of the new template has been added to the templates data file
        expected_new_tutorial_info = """{
    "slug": "blabla-bla",
    "author": "Super cantante",
    "title": "Bonita cancion",
    "videos": [
      {"id": "oPEirA4pXdg", "start": 0, "end": 999}
    ],
    "videos_full_tutorial": [],
    "full_version": "q6cUzC6ESZ8"
  }"""
        # Confirm that the list of tutorials has been updated
        with open(aprender.TUTORIALES_DATA_FILE, "r") as file:
            filedata = file.read()
        self.assertTrue(expected_new_tutorial_info in filedata)
        # Confirm that a temporary file with the content to be added to the index page has been created
        with open("../website/src/aprender/index.html", "r") as file:
            filedata = file.read()
            self.assertTrue(
                '\n              <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>'
                in filedata
            )
        # Confirm the webbrowser is called to be opened to the new template's page
        mockwbopen.assert_called_once_with(
            "http://localhost:8000/aprender/?new_tutorial=blabla-bla",
            autoraise=True,
            new=2,
        )
        # Restore the modified files
        os.remove("../website/src/aprender/index.html")
        shutil.move(
            "../website/src/aprender/index.html.bak",
            "../website/src/aprender/index.html",
        )
        os.remove(aprender.TUTORIALES_DATA_FILE)
        shutil.move(
            f"{aprender.TUTORIALES_DATA_FILE}.bak", aprender.TUTORIALES_DATA_FILE
        )

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
        (_ignore, temp_file) = tempfile.mkstemp()
        website.WEBSITE_DATA_FILE = temp_file

        # Create a copy of the index.html file that is going to be edited
        (_ignore, temp_index_file) = tempfile.mkstemp()
        shutil.copy("../website/src/index.html", temp_index_file)

        # Run the init(), will run the full --website branch
        target.init()

        # Restore the index page
        os.remove("../website/src/index.html")
        shutil.move(temp_index_file, "../website/src/index.html")

        # TODO Assert final script result
        # Delete the temporary file created by the test
        os.remove(temp_file)


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """Validate that the project has a LICENSE file, check part of its content"""
        self.assertTrue(os.path.isfile("LICENSE"))
        with open("LICENSE") as f:
            s = f.read()
            # Confirm it is the GNU Affero General Public License version 3
            self.assertTrue(
                "GNU AFFERO GENERAL PUBLIC LICENSE\n                       Version 3"
                in s
            )

    def test_license_mention(self):
        """Validate that the script file contain a mention of the license"""
        with open("vallenato_fr.py") as f:
            s = f.read()
            # Confirm it is the GNU Affero General Public License version 3
            self.assertTrue(
                "#    This file is part of Vallenato.fr.\n"
                "#\n"
                "#    Vallenato.fr is free software: you can redistribute it and/or modify\n"
                "#    it under the terms of the GNU Affero General Public License as published by\n"
                "#    the Free Software Foundation, either version 3 of the License, or\n"
                "#    (at your option) any later version.\n" in s
            )


if __name__ == "__main__":
    unittest.main()
