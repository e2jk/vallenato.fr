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
import tempfile
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
        sample_uploaded_videos_dump_file = "tests/data/sample_uploaded_videos_dump_full.json"
        uploaded_videos = website.get_dumped_uploaded_videos(sample_uploaded_videos_dump_file)
        with open(sample_uploaded_videos_dump_file) as in_file:
            expected_uploaded_videos = json.load(in_file)
        self.assertEqual(uploaded_videos, expected_uploaded_videos)

    def test_get_dumped_uploaded_videos_nonexisting_file(self):
        uploaded_videos = website.get_dumped_uploaded_videos("")
        self.assertEqual(uploaded_videos, [])

    def test_get_dumped_uploaded_videos_nonjson_file(self):
        with self.assertRaises(json.decoder.JSONDecodeError) as cm:
            uploaded_videos = website.get_dumped_uploaded_videos("templates/aprender/tutorial.html")
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
        uploaded_videos = website.get_uploaded_videos(args, "tests/data/sample_uploaded_videos_dump_full.json")
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
        uploaded_videos = website.get_uploaded_videos(args, "tests/data/sample_uploaded_videos_dump_full.json")
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
            uploaded_videos = website.get_uploaded_videos(args, "tests/data/sample_uploaded_videos_dump_full.json")
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
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        yt_lmuv.return_value = sample_uploaded_videos
        args = target.parse_args(['--website', '--dump-uploaded-videos'])

        temp_uploaded_videos_dump_file = "tests/data/temp_uploaded_videos_dump.json"
        self.assertFalse(os.path.exists(temp_uploaded_videos_dump_file))
        uploaded_videos = website.get_uploaded_videos(args, temp_uploaded_videos_dump_file)
        self.assertTrue(os.path.exists(temp_uploaded_videos_dump_file))
        self.assertEqual(uploaded_videos, sample_uploaded_videos)

        # Delete the temporary file created by the test
        os.remove(temp_uploaded_videos_dump_file)


class TestIdentifyLocationsNames(unittest.TestCase):
    def test_identify_locations_names(self):
        uploaded_videos = [{ "id": "KASEblFElVM",
             "title": "Oye Bonita, desde Buesaco, Nariño, Colombia"},
            {"id": "eEmtEtFgu94",
             "title": "Muere una Flor, desde La Cristalina, Nari\u00f1o, Colombia"}]
        (uploaded_videos, locations) = website.identify_locations_names(uploaded_videos, "tests/data/sample_location_special_cases_partial.json", "")
        # Validate that "location" has been added, with the right value
        self.assertEqual(uploaded_videos[0]["location"], "Buesaco, Nariño, Colombia")
        # Validate that the list of identified locations is as expected
        expected_locations = {'Buesaco, Nariño, Colombia': {'latitude': None, 'longitude': None},
                              'La Cristalina, Nariño, Colombia': {'latitude': None, 'longitude': None}}
        self.assertEqual(locations, expected_locations)

    def test_identify_locations_names_incomplete_locations(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        temp_uploaded_videos_dump_file = "tests/data/temp_uploaded_videos_dump.json"
        self.assertFalse(os.path.exists(temp_uploaded_videos_dump_file))
        with self.assertRaises(SystemExit) as cm:
            (uploaded_videos, locations) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_partial.json", temp_uploaded_videos_dump_file)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 20)
        self.assertTrue(os.path.exists(temp_uploaded_videos_dump_file))

        # Delete the temporary file created by the test
        os.remove(temp_uploaded_videos_dump_file)


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
        location_special_cases_file = "tests/data/sample_location_special_cases_partial.json"
        with open(location_special_cases_file) as in_file:
            special_cases = json.load(in_file)
        self.assertFalse(", desde " in vid["title"])
        self.assertFalse(", cerca de " in vid["title"])
        location = website.identify_single_location_name(vid, special_cases)
        self.assertEqual(location, "Pasto, Nariño, Colombia")

    def test_identify_single_location_name_new_special_case(self):
        vid = { "id": "uK4t2nNiySw",
                "title": "Vallenato at Epic, Verona, Wisconsin, USA"}
        location_special_cases_file = "tests/data/sample_location_special_cases_partial.json"
        with open(location_special_cases_file) as in_file:
            special_cases = json.load(in_file)
        self.assertFalse(", desde " in vid["title"])
        self.assertFalse(", cerca de " in vid["title"])
        location = website.identify_single_location_name(vid, special_cases)
        self.assertEqual(location, None)


class TestDetermineGeolocation(unittest.TestCase):
    def test_determine_geolocation(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        temp_uploaded_videos_dump_file = "tests/data/sample_uploaded_videos_dump_full.json"
        (uploaded_videos, locations) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_full.json", temp_uploaded_videos_dump_file)
        # Create a copy of the file that is going to be edited
        shutil.copy("tests/data/sample_geolocations_partial.json", "tests/data/sample_geolocations_partial.json.bak")
        with self.assertRaises(SystemExit) as cm:
            locations = website.determine_geolocation(locations, "tests/data/sample_geolocations_partial.json")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 21)
        # Restore the file
        os.remove("tests/data/sample_geolocations_partial.json")
        shutil.move("tests/data/sample_geolocations_partial.json.bak", "tests/data/sample_geolocations_partial.json")


class TestAddVideosToLocationsArray(unittest.TestCase):
    def test_add_videos_to_locations_array(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        (uploaded_videos, ignore) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_full.json", None)
        with open("tests/data/sample_geolocations_full.json") as in_file:
            locations = json.load(in_file)
        locations = website.add_videos_to_locations_array(uploaded_videos, locations)
        self.assertEqual(len(locations["Winterberg, Alemania"]["videos"]), 1)
        self.assertEqual(len(locations["Aroeira, Portugal"]["videos"]), 3)
        self.assertEqual(len(locations["Niagara Falls, Ontario, Canada"]["videos"]), 1)
        self.assertEqual(len(locations["Providencia, Colombia"]["videos"]), 13)


class TestSaveWebsiteData(unittest.TestCase):
    def test_save_website_data(self):
        (ignore, temp_file) = tempfile.mkstemp()
        with open("tests/data/sample_locations_final_full.json") as in_file:
            locations = json.load(in_file)
        website.save_website_data(locations, temp_file)

        with open(temp_file) as in_file:
            content = in_file.readlines()
        # Check that it starts with the JS bits (and not JSON)
        self.assertEqual(content[0], "var locations = {\n")
        self.assertEqual(content[-1], "};")
        # Check some random lines
        self.assertEqual(content[10], "        \"tags\": [\n")
        self.assertEqual(content[63], "        \"title\": \"Esa, desde Aroeira, Portugal\"\n")
        self.assertEqual(content[309], "        \"description\": \"Para aprender a tocar esta canci\\u00f3n: https://vallenato.fr/aprender/la-creciente.html\\nCimarrones, Nari\\u00f1o, Colombia, 08/08/2019\\nLa Creciente - Binomio de Oro\",\n")
        # Delete the temporary file created by the test
        os.remove(temp_file)


class TestWebsite(unittest.TestCase):
    @patch("website.get_uploaded_videos")
    def test_website(self, w_guv):
        # Mock valid list of videos
        with open("tests/data/sample_uploaded_videos_dump_partial.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        w_guv.return_value = sample_uploaded_videos
        # Redirect the output to a temporary file
        (ignore, temp_file) = tempfile.mkstemp()
        website.WEBSITE_DATA_FILE = temp_file
        website.website(None)
        #TODO Assert final script result
        # Delete the temporary file created by the test
        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
