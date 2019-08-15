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
import json
from youtube import HttpError
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call

sys.path.append('.')
target = __import__("vallenato_fr")
website = __import__("website")
youtube = __import__("youtube")


class TestGetDumpedUploadedVideos(unittest.TestCase):
    def test_get_dumped_uploaded_videos_valid_file(self):
        sample_uploaded_videos_dump_file = "tests/data/sample_uploaded_videos_dump.txt"
        uploaded_videos = website.get_dumped_uploaded_videos(sample_uploaded_videos_dump_file)
        with open(sample_uploaded_videos_dump_file) as in_file:
            expected_uploaded_videos = json.load(in_file)
        self.assertEqual(uploaded_videos, expected_uploaded_videos)

    def test_get_dumped_uploaded_videos_nonexisting_file(self):
        uploaded_videos = website.get_dumped_uploaded_videos("")
        self.assertEqual(uploaded_videos, [])

    def test_get_dumped_uploaded_videos_nonjson_file(self):
        with self.assertRaises(json.decoder.JSONDecodeError) as cm:
            uploaded_videos = website.get_dumped_uploaded_videos("template.html")
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Expecting value: line 1 column 1 (char 0)")


class TestGetUploadedVideos(unittest.TestCase):
    @patch("website.yt_list_my_uploaded_videos")
    @patch("website.yt_get_authenticated_service")
    @patch("website.get_dumped_uploaded_videos")
    def test_get_uploaded_videos_normal(self, w_gduv, yt_gas, yt_lmuv):
        # Ensure website.get_dumped_uploaded_videos returns []
        w_gduv.return_value = []
        args = target.parse_args(['--website'])
        uploaded_videos = website.get_uploaded_videos(args)
        self.assertTrue(call('UU_8R235jg1ld6MCMOzz2khQ', yt_gas()) in yt_lmuv.mock_calls)

    @patch("website.yt_get_my_uploads_list")
    @patch("website.yt_get_authenticated_service")
    @patch("website.get_dumped_uploaded_videos")
    def test_get_uploaded_videos_no_uploads_playlist(self, w_gduv, yt_gas, yt_gmul):
        # Ensure website.get_dumped_uploaded_videos returns []
        w_gduv.return_value = []
        # Ensure no uploads playlist was identified
        yt_gmul.return_value = None
        args = target.parse_args(['--website'])
        uploaded_videos = website.get_uploaded_videos(args)
        self.assertEqual(uploaded_videos, [])

    @patch("website.yt_get_my_uploads_list")
    @patch("website.yt_get_authenticated_service")
    @patch("website.get_dumped_uploaded_videos")
    def test_get_uploaded_videos_http_error(self, w_gduv, yt_gas, yt_gmul):
        # Ensure website.get_dumped_uploaded_videos returns []
        w_gduv.return_value = []
        # Cause an HttpError exception
        resp = MagicMock()
        yt_gmul.side_effect = HttpError(resp, b'')
        args = target.parse_args(['--website'])
        with self.assertRaises(SystemExit) as cm:
            uploaded_videos = website.get_uploaded_videos(args)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 19)

    @patch("website.yt_list_my_uploaded_videos")
    @patch("website.yt_get_my_uploads_list")
    @patch("website.yt_get_authenticated_service")
    @patch("website.get_dumped_uploaded_videos")
    def test_get_uploaded_videos_dump_uploaded_videos(self, w_gduv, yt_gas, yt_gmul, yt_lmuv):
        # Ensure website.get_dumped_uploaded_videos returns []
        w_gduv.return_value = []
        # Ensure website.get_dumped_uploaded_videos returns valid content
        with open("tests/data/sample_uploaded_videos_dump.txt") as in_file:
            sample_uploaded_videos = json.load(in_file)
        yt_lmuv.return_value = sample_uploaded_videos
        args = target.parse_args(['--website', '--dump-uploaded-videos'])

        # Move the uploaded_videos_dump.txt file as a backup copy, if it exists
        backup_created = False
        if os.path.exists("uploaded_videos_dump.txt"):
            backup_created = True
            shutil.move("uploaded_videos_dump.txt", "uploaded_videos_dump.txt.bak")

        self.assertFalse(os.path.exists("uploaded_videos_dump.txt"))
        uploaded_videos = website.get_uploaded_videos(args)
        self.assertTrue(os.path.exists("uploaded_videos_dump.txt"))
        self.assertEqual(uploaded_videos, sample_uploaded_videos)

        # Delete the file created by the test
        os.remove("uploaded_videos_dump.txt")
        if backup_created:
            # Restore the backup, if made
            shutil.move("uploaded_videos_dump.txt.bak", "uploaded_videos_dump.txt")


class TestIdentifyLocationsNames(unittest.TestCase):
    def test_identify_locations_names(self):
        uploaded_videos = [{ "id": "KASEblFElVM",
                    "title": "Oye Bonita, desde Buesaco, Nariño, Colombia"}]
        uploaded_videos = website.identify_locations_names(uploaded_videos, "tests/data/sample_location_special_cases.json")
        # Validate that "location" has been added, with the right value
        self.assertEqual(uploaded_videos[0]["location"], "Buesaco, Nariño, Colombia")

    def test_identify_locations_names_incomplete_locations(self):
        with open("tests/data/sample_uploaded_videos_dump.txt") as in_file:
            sample_uploaded_videos = json.load(in_file)
        with self.assertRaises(SystemExit) as cm:
            uploaded_videos = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases.json")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 20)


class TestIdentifySingleLocationName(unittest.TestCase):
    def test_identify_single_location_name_simple(self):
        vid = { "id": "KASEblFElVM",
                "title": "Oye Bonita, desde Buesaco, Nariño, Colombia"}
        self.assertTrue(", desde " in vid["title"])
        location = website.identify_single_location_name(vid, {})
        self.assertEqual(location, "Buesaco, Nariño, Colombia")

    def test_identify_single_location_name_special_case(self):
        vid = { "id": "oPEirA4pXdg",
                "title": "La Guaneña y el Son Sureño, ¡en vivo!"}
        location_special_cases_file = "tests/data/sample_location_special_cases.json"
        with open(location_special_cases_file) as in_file:
            special_cases = json.load(in_file)
        self.assertFalse(", desde " in vid["title"])
        self.assertFalse(", cerca de " in vid["title"])
        location = website.identify_single_location_name(vid, special_cases)
        self.assertEqual(location, "Pasto, Nariño, Colombia")

    def test_identify_single_location_name_new_special_case(self):
        vid = { "id": "uK4t2nNiySw",
                "title": "Vallenato at Epic, Verona, Wisconsin, USA"}
        location_special_cases_file = "tests/data/sample_location_special_cases.json"
        with open(location_special_cases_file) as in_file:
            special_cases = json.load(in_file)
        self.assertFalse(", desde " in vid["title"])
        self.assertFalse(", cerca de " in vid["title"])
        location = website.identify_single_location_name(vid, special_cases)
        self.assertEqual(location, None)


class TestWebsite(unittest.TestCase):
    @patch("website.get_uploaded_videos")
    def test_website(self, w_guv):
        # Mock valid list of videos
        with open("tests/data/sample_uploaded_videos_dump.txt") as in_file:
            sample_uploaded_videos = json.load(in_file)
        w_guv.return_value = sample_uploaded_videos
        website.website(None)


if __name__ == '__main__':
    unittest.main()
