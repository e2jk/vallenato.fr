#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://realpython.com/python-testing/

# Running the tests:
# $ python -m unittest -v test
# Checking the coverage of the tests:
# $ coverage run --include=vallenato_fr.py tests/test.py && coverage html

import unittest
import sys
import os

sys.path.append('.')
target = __import__("vallenato_fr")

# Used to test manual entry
mock_raw_input_counter = 0
mock_raw_input_values = []
def mock_raw_input(s):
    global mock_raw_input_counter
    global mock_raw_input_values
    mock_raw_input_counter += 1
    return mock_raw_input_values[mock_raw_input_counter - 1]
target.input = mock_raw_input

class TestGetTutorialInfo(unittest.TestCase):
    def test_get_tutorial_info(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
            "Bonita cancion",
            "Super cantante",
            "blabla-bla"
        ]
        (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, tutorial_slug) = target.get_tutorial_info()
        self.assertEqual(tutorial_id, "oPEirA4pXdg")
        self.assertEqual(tutorial_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")
        self.assertEqual(full_video_id, "q6cUzC6ESZ8")
        self.assertEqual(full_video_url, "https://www.youtube.com/watch?v=q6cUzC6ESZ8")
        self.assertEqual(song_title, "Bonita cancion")
        self.assertEqual(song_author, "Super cantante")
        self.assertEqual(tutocreator, "El Vallenatero Francés")
        self.assertEqual(tutocreator_channel, "UC_8R235jg1ld6MCMOzz2khQ")
        # Get the path of the folder two level `up tests` and `bin` (where all
        # the tutorials are)
        tutorials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        expected_slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % mock_raw_input_values[4]))
        self.assertEqual(tutorial_slug, expected_slug_path)


class TestGetYoutubeUrl(unittest.TestCase):
    def test_get_youtube_url_valid(self):
        # Pass it a valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["https://youtu.be/oPEirA4pXdg"]
        (video_id, video_url) = target.get_youtube_url("")
        self.assertEqual(video_id, "oPEirA4pXdg")
        self.assertEqual(video_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")

    def test_get_youtube_url_invalid_then_valid(self):
        # Pass it a valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ZZZ", "abc", "https://youtu.be/oPEirA4pXdg"]
        (video_id, video_url) = target.get_youtube_url("")
        self.assertEqual(video_id, "oPEirA4pXdg")
        self.assertEqual(video_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")

    def test_get_youtube_url_quit(self):
        # Entering "q" will make the script exit with value 10
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        with self.assertRaises(SystemExit) as cm:
            (video_id, video_url) = target.get_youtube_url("")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 10)


class TestYoutubeUrlValidation(unittest.TestCase):
    def test_youtube_url_validation_true(self):
        valid_youtube_urls = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "http://youtu.be/oPEirA4pXdg",
            "http://www.youtube.com/embed/oPEirA4pXdg?rel=0\" frameborder=\"0\"",
            "https://www.youtube-nocookie.com/v/oPEirA4pXdg?version=3&amp;hl=en_US",
            "https://www.youtube.com/watch?v=oPEirA4pXdg&list=PLZiwcAOEEWBqhsycvvZnBrz5Sw3yXCyRB&index=2&t=0s"
        ]
        for url in valid_youtube_urls:
            self.assertTrue(target.youtube_url_validation(url))

    def test_youtube_url_validation_false(self):
        invalid_youtube_urls = [
            "http://www.youtube.com/",
            "http://www.youtube.com/?feature=ytca",
            "https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ"
        ]
        for url in invalid_youtube_urls:
            self.assertFalse(target.youtube_url_validation(url))


class TestGetTitleAuthorTutocreatorAndChannel(unittest.TestCase):
    def test_get_title_author_tutocreator_and_channel_valid(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "DEF"]
        (song_title, song_author, tutocreator, tutocreator_channel) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        self.assertEqual(song_title, "ABC")
        self.assertEqual(song_author, "DEF")
        self.assertEqual(tutocreator, "FZ Academia Vallenato")
        self.assertEqual(tutocreator_channel, "UCWVRD_dZ2wnm1Xf_R5G0D8w")

    def test_get_title_author_tutocreator_and_channel_quit_title(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        with self.assertRaises(SystemExit) as cm:
            (song_title, song_author, tutocreator, tutocreator_channel) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 11)

    def test_get_title_author_tutocreator_and_channel_quit_author(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "q"]
        with self.assertRaises(SystemExit) as cm:
            (song_title, song_author, tutocreator, tutocreator_channel) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 12)


class TestRlinput(unittest.TestCase):
    def test_rlinput(self):
        # Since we're using a mock function to test input(), rlinput() can also
        # not really be tested...
        # It gets mock-tested through TestGetTitleAndAuthor.
        pass


class TestGetTutorialSlug(unittest.TestCase):
    def test_get_tutorial_slug_new(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["blabla-bla"]
        tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        # Get the path of the folder two level `up tests` and `bin` (where all
        # the tutorials are)
        tutorials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        expected_slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % mock_raw_input_values[0]))
        self.assertEqual(tutorial_slug, expected_slug_path)

    def test_get_tutorial_slug_existing(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["muere-una-flor", "muere-una-flor-2"]
        tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        # Get the path of the folder two level `up tests` and `bin` (where all
        # the tutorials are)
        tutorials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        expected_slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % mock_raw_input_values[1]))
        self.assertEqual(tutorial_slug, expected_slug_path)

    def test_get_tutorial_slug_existing_double(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["jaime-molina-1", "jaime-molina-2", "jaime-molina-3"]
        # We start directly at jaime-molina-1, when not using the mock version
        # the slug would already have detected there is no jaime-molina but
        # there is already a jaime-molina-1
        tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        # Get the path of the folder two level `up tests` and `bin` (where all
        # the tutorials are)
        tutorials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        expected_slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % mock_raw_input_values[2]))
        self.assertEqual(tutorial_slug, expected_slug_path)

    def test_get_tutorial_slug_quit_direct(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        with self.assertRaises(SystemExit) as cm:
            tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 13)


    def test_get_tutorial_slug_quit_second_pass(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["muere-una-flor", "q"]
        # We use a slug that already exists, then quit at the second prompt
        with self.assertRaises(SystemExit) as cm:
            tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 14)


class TestGetSuggestedTutorialSlug(unittest.TestCase):
    def test_get_suggested_tutorial_slug_new(self):
        (tutorials_path, tutorial_slug) = target.get_suggested_tutorial_slug("blabla bla")
        self.assertEqual(tutorial_slug, "blabla-bla")

    def test_get_suggested_tutorial_slug_existing(self):
        (tutorials_path, tutorial_slug) = target.get_suggested_tutorial_slug("Muere una Flor")
        # There is already a tutorial with slug muere-una-flor
        self.assertEqual(tutorial_slug, "muere-una-flor-2")

    def test_get_suggested_tutorial_slug_existing_double(self):
        (tutorials_path, tutorial_slug) = target.get_suggested_tutorial_slug("Jaime Molina")
        # There are already two tutorials jaime-molina-1 and jaime-molina-2
        self.assertEqual(tutorial_slug, "jaime-molina-3")


class TestInitMain(unittest.TestCase):
    def test_init_main_no_arguments(self):
        """
        Test the initialization code without any parameter
        """
        # Make the script believe we ran it directly
        target.__name__ = "__main__"
        # Pass it no arguments
        target.sys.argv = ["scriptname.py"]
        # Pass it two valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
            "Bonita cancion",
            "Super cantante",
            "blabla-bla"
        ]
        # Run the init(), nothing specific should happen, the program exits correctly
        target.init()


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
