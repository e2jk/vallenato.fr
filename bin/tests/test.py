#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://realpython.com/python-testing/

# Running the tests:
# $ python -m unittest -v test
# Checking the coverage of the tests:
# $ coverage run --include=vallenato_fr.py tests/test.py && coverage html

import unittest
import sys

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


class TestGetTitleAndAuthor(unittest.TestCase):
    def test_get_title_and_author_valid(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "DEF"]
        (song_title, song_author) = target.get_title_and_author("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        self.assertEqual(song_title, "ABC")
        self.assertEqual(song_author, "DEF")

    def test_get_title_and_author_quit_title(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        with self.assertRaises(SystemExit) as cm:
            (song_title, song_author) = target.get_title_and_author("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 11)

    def test_get_title_and_author_quit_author(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "q"]
        with self.assertRaises(SystemExit) as cm:
            (song_title, song_author) = target.get_title_and_author("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 12)


class TestRlinput(unittest.TestCase):
    def test_rlinput(self):
        # Since we're using a mock function to test input(), rlinput() can also
        # not really be tested...
        # It gets mock-tested through TestGetTitleAndAuthor.
        pass


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
            "",
            ""
        ]
        # Run the init(), nothing specific should happen, the program exits correctly
        target.init()

if __name__ == '__main__':
    unittest.main()
