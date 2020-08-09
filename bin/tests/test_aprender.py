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
import tempfile
from pytube import YouTube
import socket
import io
import contextlib
from urllib.error import URLError
from urllib.error import HTTPError
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call

sys.path.append('.')
target = __import__("vallenato_fr")
aprender = __import__("aprender")

# Used to test manual entry
def setUpModule():
    def mock_raw_input(s):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter += 1
        return mock_raw_input_values[mock_raw_input_counter - 1]
    aprender.input = mock_raw_input


class TestGetTutorialInfo(unittest.TestCase):
    @patch("aprender.get_title_author_tutocreator_and_channel")
    def test_get_tutorial_info(self, a_gtatac):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = [
            "http://www.youtube.com/watch?v=oPEirA4pXdg",
            "https://www.youtube.com/watch?v=q6cUzC6ESZ8",
            "blabla-bla"
        ]
        a_gtatac.return_value = ("Bonita cancion", "Super cantante", "El Vallenatero Francés", "UC_8R235jg1ld6MCMOzz2khQ", None)
        (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video, tutorial_slug) = aprender.get_tutorial_info()
        self.assertEqual(tutorial_id, "oPEirA4pXdg")
        self.assertEqual(tutorial_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")
        self.assertEqual(full_video_id, "q6cUzC6ESZ8")
        self.assertEqual(full_video_url, "https://www.youtube.com/watch?v=q6cUzC6ESZ8")
        self.assertEqual(song_title, "Bonita cancion")
        self.assertEqual(song_author, "Super cantante")
        self.assertEqual(tutocreator, "El Vallenatero Francés")
        self.assertEqual(tutocreator_channel, "UC_8R235jg1ld6MCMOzz2khQ")
        self.assertEqual(tutorial_slug, mock_raw_input_values[2])


class TestGetYoutubeUrl(unittest.TestCase):
    def test_get_youtube_url_valid(self):
        # Pass it a valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["https://youtu.be/oPEirA4pXdg"]
        (video_id, video_url) = aprender.get_youtube_url("")
        self.assertEqual(video_id, "oPEirA4pXdg")
        self.assertEqual(video_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")

    def test_get_youtube_url_invalid_then_valid(self):
        # Pass it a valid YouTube URLs
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ZZZ", "abc", "https://youtu.be/oPEirA4pXdg"]
        (video_id, video_url) = aprender.get_youtube_url("")
        self.assertEqual(video_id, "oPEirA4pXdg")
        self.assertEqual(video_url, "https://www.youtube.com/watch?v=oPEirA4pXdg")

    def test_get_youtube_url_quit(self):
        # Entering "q" will make the script exit with value 10
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            (video_id, video_url) = aprender.get_youtube_url("")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 10)
        self.assertEqual("Exiting...\n", f.getvalue())


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
            self.assertTrue(aprender.youtube_url_validation(url))

    def test_youtube_url_validation_short_id_valid(self):
        self.assertEqual(aprender.youtube_url_validation("oPEirA4pXdg"), "oPEirA4pXdg")

    def test_youtube_url_validation_false(self):
        invalid_youtube_urls = [
            "http://www.youtube.com/",
            "http://www.youtube.com/?feature=ytca",
            "https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ",
            "oPEirA4pXdgINVALID"
        ]
        for url in invalid_youtube_urls:
            self.assertFalse(aprender.youtube_url_validation(url))


class TestGetTitleAuthorTutocreatorAndChannel(unittest.TestCase):
    @patch("aprender.YouTube")
    def test_get_title_author_tutocreator_and_channel_valid(self, a_yt):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "DEF"]
        # Mock the return value of calling YouTube, to prevent lengthy network operations
        a_yt().title = "AAA"
        a_yt().author = "FZ Academia Vallenato"
        (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = aprender.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        self.assertEqual(song_title, "ABC")
        self.assertEqual(song_author, "DEF")
        self.assertEqual(tutocreator, "FZ Academia Vallenato")
        self.assertEqual(tutocreator_channel, "UPDATE MANUALLY")

    @patch("aprender.YouTube")
    def test_get_title_author_tutocreator_and_channel_quit_title(self, a_yt):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = aprender.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 11)
        self.assertEqual("Exiting...\n", f.getvalue())

    @patch("aprender.YouTube")
    def test_get_title_author_tutocreator_and_channel_quit_author(self, a_yt):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["ABC", "q"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = aprender.get_title_author_tutocreator_and_channel("https://www.youtube.com/watch?v=v5xEaLCCNRc")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 12)
        self.assertEqual("Exiting...\n", f.getvalue())


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
        tutorial_slug = aprender.get_tutorial_slug("NOT RELEVANT")
        self.assertEqual(tutorial_slug, mock_raw_input_values[0])

    def test_get_tutorial_slug_existing(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["muere-una-flor", "muere-una-flor-2"]
        tutorial_slug = aprender.get_tutorial_slug("NOT RELEVANT")
        self.assertEqual(tutorial_slug, mock_raw_input_values[1])

    def test_get_tutorial_slug_existing_double(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["jaime-molina-1", "jaime-molina-2", "jaime-molina-3"]
        # We start directly at jaime-molina-1, when not using the mock version
        # the slug would already have detected there is no jaime-molina but
        # there is already a jaime-molina-1
        tutorial_slug = aprender.get_tutorial_slug("NOT RELEVANT")
        self.assertEqual(tutorial_slug, mock_raw_input_values[2])

    def test_get_tutorial_slug_quit_direct(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["q"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            tutorial_slug = aprender.get_tutorial_slug("NOT RELEVANT")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 13)
        self.assertEqual("Exiting...\n", f.getvalue())

    def test_get_tutorial_slug_quit_second_pass(self):
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["muere-una-flor", "q"]
        # We use a slug that already exists, then quit at the second prompt
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            tutorial_slug = aprender.get_tutorial_slug("NOT RELEVANT")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 14)
        self.assertEqual("Exiting...\n", f.getvalue())


class TestGetSuggestedTutorialSlug(unittest.TestCase):
    def test_get_suggested_tutorial_slug_new(self):
        tutorials_slugs = aprender.get_existing_tutorial_slug()
        tutorial_slug = aprender.get_suggested_tutorial_slug("blabla bla", tutorials_slugs)
        self.assertEqual(tutorial_slug, "blabla-bla")

    def test_get_suggested_tutorial_slug_existing(self):
        tutorials_slugs = aprender.get_existing_tutorial_slug()
        tutorial_slug = aprender.get_suggested_tutorial_slug("Muere una Flor", tutorials_slugs)
        # There is already a tutorial with slug muere-una-flor
        self.assertEqual(tutorial_slug, "muere-una-flor-2")

    def test_get_suggested_tutorial_slug_existing_double(self):
        tutorials_slugs = aprender.get_existing_tutorial_slug()
        tutorial_slug = aprender.get_suggested_tutorial_slug("Jaime Molina", tutorials_slugs)
        # There are already two tutorials jaime-molina-1 and jaime-molina-2
        self.assertEqual(tutorial_slug, "jaime-molina-3")


class TestDetermineOutputFolder(unittest.TestCase):
    def test_determine_output_folder_no_temp_folder(self):
        temp_folder = False
        tutorial_slug = None
        output_folder = aprender.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../website/src/aprender/")

    def test_determine_output_folder_temp_folder_doesnt_exist(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        # Make sure the new temporary folder doesn't exist
        if os.path.exists("../website/src/aprender/temp/blabla-bla/"):
            shutil.rmtree("../website/src/aprender/temp/blabla-bla/")
        output_folder = aprender.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../website/src/aprender/temp/blabla-bla/")
        self.assertTrue(os.path.exists("../website/src/aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_exit(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["N"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../website/src/aprender/temp/blabla-bla/")
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            output_folder = aprender.determine_output_folder(temp_folder, tutorial_slug)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 15)
        self.assertEqual("Exiting...\n", f.getvalue())
        self.assertTrue(os.path.exists("../website/src/aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_invalid_entries(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        # Make some invalid entries
        mock_raw_input_values = ["Continue", "No", "42", "N"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../website/src/aprender/temp/blabla-bla/")
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            output_folder = aprender.determine_output_folder(temp_folder, tutorial_slug)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 15)
        self.assertEqual("Exiting...\n", f.getvalue())
        self.assertTrue(os.path.exists("../website/src/aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")

    def test_determine_output_folder_temp_folder_exists_delete(self):
        temp_folder = True
        tutorial_slug = "blabla-bla"
        global mock_raw_input_counter
        global mock_raw_input_values
        mock_raw_input_counter = 0
        mock_raw_input_values = ["y"]
        # Make sure the new temporary folder *does* exist
        os.makedirs("../website/src/aprender/temp/blabla-bla/")
        # Create a temporary file that should be deleted when the folder is deleted
        (ignore, temp_file) = tempfile.mkstemp(dir="../website/src/aprender/temp/blabla-bla/")
        self.assertTrue(os.path.exists(temp_file))
        output_folder = aprender.determine_output_folder(temp_folder, tutorial_slug)
        self.assertEqual(output_folder, "../website/src/aprender/temp/blabla-bla/")
        # Confirm the temporary file created before deleting the directory was indeed deleted
        self.assertFalse(os.path.exists(temp_file))
        self.assertTrue(os.path.exists("../website/src/aprender/temp/blabla-bla/"))
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")


class TestDownloadVideos(unittest.TestCase):
    @patch("aprender.download_youtube_video")
    @patch("aprender.YouTube")
    def test_download_videos(self, a_yt, a_dyv):
        yt_tutorial_video = MagicMock()
        tutorial_id = "KtN7MCg6hlI"
        full_video_id = "eT2Q_Go2BAs"
        videos_output_folder = "/tmp/abc"
        aprender.download_videos(yt_tutorial_video, tutorial_id, full_video_id, videos_output_folder)
        self.assertTrue(a_yt.mock_calls == [call('https://www.youtube.com/watch?v=eT2Q_Go2BAs')])
        expected = [call(yt_tutorial_video, 'KtN7MCg6hlI', '/tmp/abc'),
                    call(a_yt(), 'eT2Q_Go2BAs', '/tmp/abc')]
        self.assertTrue(a_dyv.mock_calls == expected)


class TestDownloadYoutubeVideo(unittest.TestCase):
    def test_download_youtube_video(self):
        yt = MagicMock()
        video_id = "oPEirA4pXdg"
        videos_output_folder = tempfile.mkdtemp()
        rv = aprender.download_youtube_video(yt, video_id, videos_output_folder)
        self.assertTrue(rv)
        self.assertTrue(yt.method_calls == [call.streams.get_by_itag(18)])
        self.assertTrue(call.streams.get_by_itag().download(videos_output_folder, 'oPEirA4pXdg') in yt.mock_calls)
        # Delete the temporary folder
        shutil.rmtree(videos_output_folder)

    def test_download_youtube_video_no_itag_18(self):
        yt = MagicMock()
        # Mock that there is no stream available with itag 18
        yt.streams.get_by_itag.return_value = None
        video_id = "oPEirA4pXdg"
        videos_output_folder = tempfile.mkdtemp()
        rv = aprender.download_youtube_video(yt, video_id, videos_output_folder)
        self.assertTrue(rv)
        self.assertTrue(yt.method_calls == [call.streams.get_by_itag(18), call.streams.filter(file_extension='mp4', progressive=True, res='360p')])
        self.assertTrue(call.streams.filter().first().download(videos_output_folder, 'oPEirA4pXdg') in yt.mock_calls)
        # Delete the temporary folder
        shutil.rmtree(videos_output_folder)

    @patch("aprender.download_stream")
    @patch("webbrowser.open")
    def test_download_youtube_video_HTTPError(self, mockwbopen, a_ds):
        a_ds.side_effect = HTTPError(None, 403, "Forbidden", None, None)
        yt = MagicMock()
        video_id = "NzpNsbX3uC4"
        videos_output_folder = tempfile.mkdtemp()
        with self.assertLogs(level='ERROR') as cm:
            rv = aprender.download_youtube_video(yt, video_id, videos_output_folder)
        # Confirm that an HTTPError was raised
        self.assertFalse(rv)
        self.assertEqual(cm.output, ['ERROR:root:An HTTP error 403 occurred with reason: Forbidden'])
        # Delete the temporary folder
        shutil.rmtree(videos_output_folder)


class TestDownloadStream(unittest.TestCase):
    def test_download_stream(self):
        # It gets mock-tested through TestDownloadYoutubeVideo.test_download_youtube_video_HTTPError
        pass


class TestGenerateNewTutorialInfo(unittest.TestCase):
    def test_generate_new_tutorial_info(self):
        tutorial_slug = "blabla-bla"
        song_title = "Bonita cancion"
        song_author = "Super cantante"
        tutorial_id = "oPEirA4pXdg"
        full_video_id = "q6cUzC6ESZ8"
        expected_output = """{
    "slug": "blabla-bla",
    "author": "Super cantante",
    "title": "Bonita cancion",
    "videos": [
      {"id": "oPEirA4pXdg", "start": 0, "end": 999}
    ],
    "videos_full_tutorial": [],
    "full_version": "q6cUzC6ESZ8"
  }"""
        new_tutorial_info = aprender.generate_new_tutorial_info(tutorial_slug, song_author, song_title, tutorial_id, full_video_id)
        self.assertEqual(new_tutorial_info, expected_output)


class TestUpdateTutorialesDataFile(unittest.TestCase):
    def test_update_tutoriales_data_file(self):
        tutorial_slug = "blabla-bla"
        song_title = "Bonita cancion"
        song_author = "Super cantante"
        tutorial_id = "oPEirA4pXdg"
        full_video_id = "q6cUzC6ESZ8"
        expected_output = """{
    "slug": "blabla-bla",
    "author": "Super cantante",
    "title": "Bonita cancion",
    "videos": [
      {"id": "oPEirA4pXdg", "start": 0, "end": 999}
    ],
    "videos_full_tutorial": [],
    "full_version": "q6cUzC6ESZ8"
  }"""
        new_tutorial_info = aprender.generate_new_tutorial_info(tutorial_slug, song_author, song_title, tutorial_id, full_video_id)
        self.assertEqual(new_tutorial_info, expected_output)
        # Copy the content of the tutoriales data file to a new temporary file
        (ignore, temp_tutoriales_data_file) = tempfile.mkstemp()
        shutil.copy(aprender.TUTORIALES_DATA_FILE, temp_tutoriales_data_file)
        aprender.update_tutoriales_data_file(temp_tutoriales_data_file, new_tutorial_info)
        # Confirm that the list of tutorials has been updated
        with open(temp_tutoriales_data_file, 'r') as file :
            filedata = file.read()
        self.assertTrue(new_tutorial_info in filedata)
        # Delete the temporary file
        os.remove(temp_tutoriales_data_file)


class TestUpdateIndexPage(unittest.TestCase):
    def test_update_index_page_ok(self):
        tutorial_slug = "blabla-bla"
        song_title = "Bonita cancion"
        song_author = "Super cantante"
        tutorial_url = "https://www.youtube.com/watch?v=oPEirA4pXdg"
        tutocreator_channel = "UC_8R235jg1ld6MCMOzz2khQ"
        tutocreator = "El Vallenatero Francés"
        # Create a copy of the index.html file that is going to be edited
        shutil.copy("../website/src/aprender/index.html", "../website/src/aprender/index.html.bak")
        aprender.update_index_page(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)
        # Confirm that the index page has been updated
        with open("../website/src/aprender/index.html", 'r') as file :
            filedata = file.read()
            self.assertTrue('</a></li>\n              <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>\n            </ul>' in filedata)
        # Restore the index page
        os.remove("../website/src/aprender/index.html")
        shutil.move("../website/src/aprender/index.html.bak", "../website/src/aprender/index.html")


class TestAprender(unittest.TestCase):
    @patch("aprender.get_title_author_tutocreator_and_channel")
    @patch("webbrowser.open")
    def test_init_main_aprender_temp_folder_no_download(self, mockwbopen, a_gtatac):
        """
        Test the full --aprender branch, with the --temp-folder and --no-download parameters
        """
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
        # Run the main --aprender code branch
        args = target.parse_args(['--aprender', "--temp-folder", "--no-download"])
        aprender.aprender(args)
        # Confirm that the info of the new template has been added to the templates data file
  #       #TODO use the actual temp file that was updated
  #       temp_tutoriales_data_file = aprender.TUTORIALES_DATA_FILE
  #       expected_new_tutorial_info = """{
  #   "slug": "blabla-bla",
  #   "author": "Super cantante",
  #   "title": "Bonita cancion",
  #   "videos": [
  #     {"id": "oPEirA4pXdg", "start": 0, "end": 999}
  #   ],
  #   "videos_full_tutorial": [],
  #   "full_version": "q6cUzC6ESZ8"
  # }"""
  #       # Confirm that the list of tutorials has been updated
  #       with open(temp_tutoriales_data_file, 'r') as file :
  #           filedata = file.read()
  #       self.assertTrue(expected_new_tutorial_info in filedata)
        # Confirm that a temporary file with the content to be added to the index page has been created
        with open("../website/src/aprender/temp/blabla-bla/index-dummy.html", 'r') as file :
            filedata = file.read()
            self.assertTrue("""              <div class="card mb-3" style="max-width: 17rem;">
                <div class="card-body">
                  <h5 class="card-title">Bonita cancion - Super cantante</h5>
                  <a href="blabla-bla" class="stretched-link text-hide">Ver el tutorial</a>
                </div>
                <div class="card-footer"><small class="text-muted">NNmNNs en NN partes</small></div>
              </div>""" in filedata)
            self.assertTrue('\n              <li>Bonita cancion - Super cantante: <a href="https://www.youtube.com/watch?v=oPEirA4pXdg">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/UC_8R235jg1ld6MCMOzz2khQ">El Vallenatero Francés</a></li>' in filedata)
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")
        # Confirm the webbrowser is called to be opened to the new template's page
        mockwbopen.assert_called_once_with("http://localhost:8000/aprender/?new_tutorial=blabla-bla", autoraise=True, new=2)

    @patch("aprender.get_title_author_tutocreator_and_channel")
    @patch("aprender.YouTube")
    @patch("webbrowser.open")
    def test_init_main_aprender_temp_videos_output_folder_doesnt_exist(self, mockwbopen, a_yt, a_gtatac):
        """
        Test the full --aprender branch, with --temp-folder when the temporary folder to host the downloaded videos doesn't exist yet
        """
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
        # Make sure the temporary folder to host the downloaded videos doesn't exist
        videos_output_folder = "../website/src/aprender/temp/blabla-bla/videos/blabla-bla"
        if os.path.exists(videos_output_folder):
            shutil.rmtree(videos_output_folder)
        # Run the main --aprender code branch
        args = target.parse_args(['--aprender', "--temp-folder"])
        aprender.aprender(args)
        # Confirm that the new temporary folder has been created to host the downloaded videos
        self.assertTrue(os.path.exists(videos_output_folder))
        # Delete the temporary folder
        shutil.rmtree("../website/src/aprender/temp/blabla-bla/")


if __name__ == '__main__':
    unittest.main()
