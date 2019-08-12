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
import shutil
import logging
import tempfile
from pytube import YouTube
import socket
from urllib.error import URLError
from unittest.mock import patch

sys.path.append('.')
target = __import__("vallenato_fr")

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
        if is_connected():
            (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video, tutorial_slug) = target.get_tutorial_info()
            self.assertEqual(tutorial_id, "oPEirA4pXdg")
            self.assertEqual(tutorial_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")
            self.assertEqual(full_video_id, "q6cUzC6ESZ8")
            self.assertEqual(full_video_url, "https://www.youtube.com/watch?v=q6cUzC6ESZ8")
            self.assertEqual(song_title, "Bonita cancion")
            self.assertEqual(song_author, "Super cantante")
            self.assertEqual(tutocreator, "El Vallenatero Francés")
            self.assertEqual(tutocreator_channel, "UC_8R235jg1ld6MCMOzz2khQ")
            self.assertEqual(tutorial_slug, mock_raw_input_values[4])
        else:
            with self.assertRaises(URLError) as cm:
                (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video, tutorial_slug) = target.get_tutorial_info()
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")


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
        if is_connected():
            (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            self.assertEqual(song_title, "ABC")
            self.assertEqual(song_author, "DEF")
            self.assertEqual(tutocreator, "FZ Academia Vallenato")
            self.assertEqual(tutocreator_channel, "UCWVRD_dZ2wnm1Xf_R5G0D8w")
        else:
            with self.assertRaises(URLError) as cm:
                (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")

    def test_get_title_author_tutocreator_and_channel_quit_title(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        if is_connected():
            with self.assertRaises(SystemExit) as cm:
                (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            the_exception = cm.exception
            self.assertEqual(the_exception.code, 11)
        else:
            with self.assertRaises(URLError) as cm:
                (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")

    def test_get_title_author_tutocreator_and_channel_quit_author(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "q"]
        if is_connected():
            with self.assertRaises(SystemExit) as cm:
                (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            the_exception = cm.exception
            self.assertEqual(the_exception.code, 12)
        else:
            with self.assertRaises(URLError) as cm:
                (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = target.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")


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
        self.assertEqual(tutorial_slug, mock_raw_input_values[0])

    def test_get_tutorial_slug_existing(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["muere-una-flor", "muere-una-flor-2"]
        tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        self.assertEqual(tutorial_slug, mock_raw_input_values[1])

    def test_get_tutorial_slug_existing_double(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["jaime-molina-1", "jaime-molina-2", "jaime-molina-3"]
        # We start directly at jaime-molina-1, when not using the mock version
        # the slug would already have detected there is no jaime-molina but
        # there is already a jaime-molina-1
        tutorial_slug = target.get_tutorial_slug("NOT RELEVANT")
        self.assertEqual(tutorial_slug, mock_raw_input_values[2])

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


class TestDetermineOutputFolder(unittest.TestCase):
    def test_determine_output_folder_no_temp_folder(self):
        temp_folder = False
        tutorial_slug = None
        output_folder = target.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../aprender/")

    def test_determine_output_folder_temp_folder_doesnt_exist(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        # Make sure the new temporary folder doesn't exist
        if os.path.exists("../aprender/temp/blabla-bla/"):
            shutil.rmtree("../aprender/temp/blabla-bla/")
        output_folder = target.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../aprender/temp/blabla-bla/")
        self.assertTrue(os.path.exists("../aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_exit(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["N"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../aprender/temp/blabla-bla/")
        with self.assertRaises(SystemExit) as cm:
            output_folder = target.determine_output_folder(temp_folder, tutorial_slug)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 15)
        self.assertTrue(os.path.exists("../aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_invalid_entries(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        # Make some invalid entries
        mock_raw_input_values = ["Continue", "No", "42", "N"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../aprender/temp/blabla-bla/")
        with self.assertRaises(SystemExit) as cm:
            output_folder = target.determine_output_folder(temp_folder, tutorial_slug)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 15)
        self.assertTrue(os.path.exists("../aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_delete(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["y"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../aprender/temp/blabla-bla/")
        # Create a temporary file that should be deleted when the folder is deleted
        (ignore, temp_file) = tempfile.mkstemp(dir="../aprender/temp/blabla-bla/")
        self.assertTrue(os.path.exists(temp_file))
        output_folder = target.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../aprender/temp/blabla-bla/")
        # Confirm the temporary file created before deleting the directory was indeed deleted
        self.assertFalse(os.path.exists(temp_file))
        self.assertTrue(os.path.exists("../aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../aprender/temp/blabla-bla/")


class TestDownloadYoutubeVideo(unittest.TestCase):
    def test_download_youtube_video(self):
        video_id = "oPEirA4pXdg"
        if is_connected():
            yt = YouTube("https://www.youtube.com/watch?v=%s" % video_id)
            videos_output_folder = tempfile.mkdtemp()
            parser = target.parse_args(['--debug', '--aprender'])
            target.download_youtube_video(yt, video_id, videos_output_folder)
            self.assertTrue(os.path.exists("%s/%s.mp4" % (videos_output_folder, video_id)))
            # Delete the temporary folder
            shutil.rmtree(videos_output_folder)
        else:
            with self.assertRaises(URLError) as cm:
                yt = YouTube("https://www.youtube.com/watch?v=%s" % video_id)
            self.assertEqual(str(cm.exception), "<urlopen error [Errno -2] Name or service not known>")


class TestCreateNewTutorialPage(unittest.TestCase):
    def test_create_new_tutorial_page_ok(self):
        tutorial_slug = "blabla-bla"
        song_title = "Bonita cancion"
        song_author = "Super cantante"
        tutorial_id = "oPEirA4pXdg"
        full_video_id = "q6cUzC6ESZ8"
        output_folder = "../aprender/"
        new_tutorial_page = "%s%s.html" % (output_folder, tutorial_slug)
        target.create_new_tutorial_page(tutorial_slug, song_title, song_author, tutorial_id, full_video_id, new_tutorial_page)
        # Confirm that a new tutorial page has been created
        self.assertTrue(os.path.exists("../aprender/blabla-bla.html"))
        # Confirm that the content of the new template has been updated
        with open("../aprender/blabla-bla.html", 'r') as file :
            filedata = file.read()
        self.assertTrue("<title>Bonita cancion - Super cantante</title>" in filedata)
        self.assertTrue('<span id="nameCurrent">Bonita cancion - Super cantante</span>' in filedata)
        self.assertTrue('{"id": "oPEirA4pXdg", "start": 0, "end": 999}' in filedata)
        self.assertTrue('var fullVersion = "q6cUzC6ESZ8";' in filedata)
        # Delete that new tutorial page
        os.remove("../aprender/blabla-bla.html")


class TestUpdateIndexPage(unittest.TestCase):
    def test_update_index_page_ok(self):
        tutorial_slug = "blabla-bla"
        song_title = "Bonita cancion"
        song_author = "Super cantante"
        tutorial_url = "https://www.youtube.com/watch?v=oPEirA4pXdg"
        tutocreator_channel = "UC_8R235jg1ld6MCMOzz2khQ"
        tutocreator = "El Vallenatero Francés"
        # Create a copy of the index.html file that is going to be edited
        shutil.copy("../aprender/index.html", "../aprender/index.html.bak")
        target.update_index_page(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)
        # Confirm that the index page has been updated
        with open("../aprender/index.html", 'r') as file :
            filedata = file.read()
        self.assertTrue('</li>\n      <li><a href="blabla-bla.html">Bonita cancion - Super cantante</a> - NNmNNs en NN partes</li>\n    </ul>' in filedata)
        self.assertTrue('</a></li>\n      <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>\n    </ul>' in filedata)
        # Restore the index page
        os.remove("../aprender/index.html")
        shutil.move("../aprender/index.html.bak", "../aprender/index.html")


class TestParseArgs(unittest.TestCase):
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

    @patch("webbrowser.open")
    def test_init_main_temp_folder_no_download(self, mockwbopen):
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
            "Bonita cancion",
            "Super cantante",
            "blabla-bla"
        ]
        # Run the init(), the program exits correctly
        if is_connected():
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
