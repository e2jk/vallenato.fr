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
from datetime import date
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


class TestDetermineVideosSlug(unittest.TestCase):
    def test_determine_videos_slug(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        uploaded_videos = website.determine_videos_slug(sample_uploaded_videos)
        self.assertEqual(uploaded_videos[-1]["title"], "Oye Bonita, desde Buesaco, Nariño, Colombia")
        self.assertEqual(uploaded_videos[-1]["slug"], "oye-bonita-buesaco-narino-colombia")
        self.assertEqual(uploaded_videos[-10]["title"], "Lleno de Ti, desde El Remolino, Nariño, Colombia")
        self.assertEqual(uploaded_videos[-10]["slug"], "lleno-de-ti-el-remolino-narino-colombia")
        self.assertEqual(uploaded_videos[-20]["title"], "Oye Bonita, desde Pasisara, Nariño, Colombia")
        self.assertEqual(uploaded_videos[-20]["slug"], "oye-bonita-pasisara-narino-colombia")
        self.assertEqual(uploaded_videos[-30]["title"], "La Creciente, desde San Andrés, Colombia")
        self.assertEqual(uploaded_videos[-30]["slug"], "la-creciente-san-andres-colombia")


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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(level='CRITICAL') as cm2:
            uploaded_videos = website.get_uploaded_videos(args, "tests/data/sample_uploaded_videos_dump_full.json")
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 19)
        self.assertEqual(cm2.output, ['CRITICAL:root:Exiting...'])

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
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(level='CRITICAL') as cm2:
            (uploaded_videos, locations) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_partial.json", temp_uploaded_videos_dump_file)
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 20)
        self.assertTrue(os.path.exists(temp_uploaded_videos_dump_file))
        self.assertEqual(cm2.output, ["CRITICAL:root:No Location found for uK4t2nNiySw, 'Vallenato at Epic, Verona, Wisconsin, USA'",
                                      "CRITICAL:root:Please add the new/missing location to the file 'tests/data/sample_location_special_cases_partial.json'. Exiting..."])

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
        with self.assertLogs(level='CRITICAL') as cm:
            location = website.identify_single_location_name(vid, special_cases)
        self.assertEqual(location, None)
        self.assertEqual(cm.output, ["CRITICAL:root:No Location found for uK4t2nNiySw, 'Vallenato at Epic, Verona, Wisconsin, USA'"])


class TestDetermineGeolocation(unittest.TestCase):
    def test_determine_geolocation(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        temp_uploaded_videos_dump_file = "tests/data/sample_uploaded_videos_dump_full.json"
        with self.assertLogs(level='INFO') as cm:
            (uploaded_videos, locations) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_full.json", temp_uploaded_videos_dump_file)
        self.assertEqual(cm.output, ["INFO:root:Found 22 different location name."])
        # Create a copy of the file that is going to be edited
        shutil.copy("tests/data/sample_geolocations_partial.json", "tests/data/sample_geolocations_partial.json.bak")
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(level='CRITICAL') as cm2:
            locations = website.determine_geolocation(locations, "tests/data/sample_geolocations_partial.json")
        the_exception = cm1.exception
        self.assertEqual(the_exception.code, 21)
        expected = ['CRITICAL:root:No geolocation found for París, Francia.',
            "CRITICAL:root:No geolocation found for 's-Hertogenbosch, Países Bajos.",
            'CRITICAL:root:No geolocation found for Ciudad de Panamá, Panamá.',
            'CRITICAL:root:No geolocation found for Santa Marta, Magdalena, Colombia.',
            'CRITICAL:root:No geolocation found for La Cristalina, Nariño, Colombia.',
            'CRITICAL:root:No geolocation found for Cimarrones, Nariño, Colombia.',
            'CRITICAL:root:No geolocation found for Atlanta, Georgia, USA.',
            'CRITICAL:root:No geolocation found for Verona, Wisconsin, USA.',
            'CRITICAL:root:No geolocation found for Solbach, Francia.',
            'CRITICAL:root:No geolocation found for Winterberg, Alemania.',
            'CRITICAL:root:No geolocation found for Bruselas, Belgica.',
            'CRITICAL:root:No geolocation found for Niagara Falls, Ontario, Canada.',
            'CRITICAL:root:No geolocation found for Providencia, Colombia.',
            'CRITICAL:root:No geolocation found for San Andrés, Colombia.',
            'CRITICAL:root:No geolocation found for Cali, Valle del Cauca, Colombia.',
            'CRITICAL:root:No geolocation found for Pasto, Nariño, Colombia.',
            'CRITICAL:root:No geolocation found for Pasisara, Nariño, Colombia.',
            'CRITICAL:root:No geolocation found for Lisboa, Portugal.',
            'CRITICAL:root:No geolocation found for Aroeira, Portugal.',
            'CRITICAL:root:No geolocation found for El Remolino, Nariño, Colombia.',
            'CRITICAL:root:No geolocation found for Koh Phangan, Tailandia.',
            "CRITICAL:root:Please add the 21 new/missing unknown latitude and longitude to the file 'tests/data/sample_geolocations_partial.json'. Exiting..."]
        self.assertEqual(cm2.output, expected)
        # Restore the file
        os.remove("tests/data/sample_geolocations_partial.json")
        shutil.move("tests/data/sample_geolocations_partial.json.bak", "tests/data/sample_geolocations_partial.json")


class TestAddVideosToLocationsArray(unittest.TestCase):
    def test_add_videos_to_locations_array(self):
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        with self.assertLogs(level='INFO') as cm:
            (uploaded_videos, ignore) = website.identify_locations_names(sample_uploaded_videos, "tests/data/sample_location_special_cases_full.json", None)
        self.assertEqual(cm.output, ["INFO:root:Found 22 different location name."])
        with open("tests/data/sample_geolocations_full.json") as in_file:
            locations = json.load(in_file)
        locations = website.add_videos_to_locations_array(uploaded_videos, locations)
        self.assertEqual(len(locations["Winterberg, Alemania"]["videos"]), 1)
        self.assertEqual(len(locations["Aroeira, Portugal"]["videos"]), 3)
        self.assertEqual(len(locations["Niagara Falls, Ontario, Canada"]["videos"]), 1)
        self.assertEqual(len(locations["Providencia, Colombia"]["videos"]), 13)


class TestDetermineLocationsSlug(unittest.TestCase):
    def test_determine_locations_slug(self):
        with open("tests/data/sample_geolocations_full.json") as in_file:
            locations = json.load(in_file)
        locations = website.determine_locations_slug(locations)
        self.assertEqual(locations['Solbach, Francia']["slug"],'solbach-francia')
        self.assertEqual(locations['Niagara Falls, Ontario, Canada']["slug"],'niagara-falls-ontario-canada')
        self.assertEqual(locations['Buesaco, Nariño, Colombia']["slug"],'buesaco-narino-colombia')


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
        # Delete the temporary file created by the test
        os.remove(temp_file)


class TestGetStats(unittest.TestCase):
    @patch("website.datetime.date")
    def test_get_stats_august(self, w_dd):
        w_dd.today.return_value = date(2020, 8, 13)
        w_dd.side_effect = lambda *args, **kw: date(*args, **kw)
        with open("tests/data/sample_locations_final_full.json") as in_file:
            sample_locations = json.load(in_file)
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        stats = website.get_stats(sample_locations, sample_uploaded_videos)
        self.assertEqual(stats, 'El Vallenatero Francés les presenta 84 videos de 13 canciones tocadas en 22 lugares de 10 paises. El empezo a aprender el Acordeón Vallenato en la Navidad 2017 (hace mas o menos 2 años y 8 meses).')

    @patch("website.datetime.date")
    def test_get_stats_december(self, w_dd):
        w_dd.today.return_value = date(2020, 12, 13)
        w_dd.side_effect = lambda *args, **kw: date(*args, **kw)
        with open("tests/data/sample_locations_final_full.json") as in_file:
            sample_locations = json.load(in_file)
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        stats = website.get_stats(sample_locations, sample_uploaded_videos)
        self.assertEqual(stats, 'El Vallenatero Francés les presenta 84 videos de 13 canciones tocadas en 22 lugares de 10 paises. El empezo a aprender el Acordeón Vallenato en la Navidad 2017 (hace mas o menos 3 años).')

    @patch("website.datetime.date")
    def test_get_stats_january(self, w_dd):
        w_dd.today.return_value = date(2021, 1, 13)
        w_dd.side_effect = lambda *args, **kw: date(*args, **kw)
        with open("tests/data/sample_locations_final_full.json") as in_file:
            sample_locations = json.load(in_file)
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        stats = website.get_stats(sample_locations, sample_uploaded_videos)
        self.assertEqual(stats, 'El Vallenatero Francés les presenta 84 videos de 13 canciones tocadas en 22 lugares de 10 paises. El empezo a aprender el Acordeón Vallenato en la Navidad 2017 (hace mas o menos 3 años).')


class TestGenerateWebsite(unittest.TestCase):
    @patch("website.datetime.date")
    def test_generate_website(self, w_dd):
        w_dd.today.return_value = date(2020, 8, 13)
        w_dd.side_effect = lambda *args, **kw: date(*args, **kw)
        # Create a copy of the index.html file that is going to be edited
        (ignore, temp_index_file) = tempfile.mkstemp()
        shutil.copy("../website/src/index.html", temp_index_file)

        with open("tests/data/sample_locations_final_full.json") as in_file:
            sample_locations = json.load(in_file)
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)

        website.generate_website(sample_locations, sample_uploaded_videos)

        # Confirm that the stats on the index page have been updated
        with open("../website/src/index.html", 'r') as file :
            filedata = file.read()
            self.assertTrue('<div id="stats">El Vallenatero Francés les presenta 84 videos de 13 canciones tocadas en 22 lugares de 10 paises. El empezo a aprender el Acordeón Vallenato en la Navidad 2017 (hace mas o menos 2 años y 8 meses).</div>' in filedata)
        # Restore the index page
        os.remove("../website/src/index.html")
        shutil.move(temp_index_file, "../website/src/index.html")


        # Check prod folder exist
        self.assertTrue(os.path.exists("../website/prod"))

        # Check the expected values are in the prod files
        with open("../website/prod/index.html", 'r') as file :
            index_data = file.read()
        with open("../website/prod/404.html", 'r') as file :
            page404_data = file.read()
        with open("../website/prod/aprender/index.html", 'r') as file :
            index_aprender_data = file.read()
        # The prod file points to the CDN copy of the leaflet library
        self.assertTrue('<link rel="stylesheet" href="https://unpkg.com/leaflet@%s/dist/leaflet.css"\n        integrity="sha512-' % website.LEAFLET_VERSION in index_data)
        self.assertTrue('<script src="https://unpkg.com/leaflet@%s/dist/leaflet.js"\n        integrity="sha512-' % website.LEAFLET_VERSION in index_data)
        # The prod files point to the CDN copy of the Bootstrap library
        self.assertTrue('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in index_data)
        self.assertTrue('<script src="https://stackpath.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in index_data)
        self.assertTrue('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in page404_data)
        self.assertTrue('<script src="https://stackpath.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in page404_data)
        self.assertTrue('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in index_aprender_data)
        self.assertTrue('<script src="https://stackpath.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js"\n        integrity="sha384-' % website.BOOTSTRAP_VERSION in index_aprender_data)
        # The prod files point to the CDN copy of the jQuery library
        self.assertTrue('<script src="https://code.jquery.com/jquery-%s.slim.min.js"\n        integrity="sha384-' % website.JQUERY_VERSION in index_data)
        self.assertTrue('<script src="https://code.jquery.com/jquery-%s.slim.min.js"\n        integrity="sha384-' % website.JQUERY_VERSION in page404_data)
        self.assertTrue('<script src="https://code.jquery.com/jquery-%s.slim.min.js"\n        integrity="sha384-' % website.JQUERY_VERSION in index_aprender_data)
        # The prod files point to the CDN copy of the Bootstrap-toggle library
        self.assertTrue('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@%s/css/bootstrap4-toggle.min.css"\n        integrity="sha384-' % website.BOOTSTRAP_TOGGLE_VERSION in index_aprender_data)
        self.assertTrue('<script src="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@%s/js/bootstrap4-toggle.min.js"\n        integrity="sha384-' % website.BOOTSTRAP_TOGGLE_VERSION in index_aprender_data)
        # Copyright year in the pages' footer
        # datetime.date.today is patched to return a date in 2020
        expected_value = '<span class="text-muted">&copy; 2020 El Vallenatero Francés</span>'
        for page_data in (index_data, page404_data, index_aprender_data):
            self.assertTrue(expected_value in page_data)

        # Confirm the local copies of the libraries are not present in the prd folder
        # (sitemap.xml gets generated in a later step)
        expected_prd_files = ['404.html',
                              'android-chrome-192x192.png',
                              'android-chrome-512x512.png',
                              'apple-touch-icon.png',
                              'aprender',
                              'browserconfig.xml',
                              'data.js',
                              'favicon.ico',
                              'favicon-16x16.png',
                              'favicon-32x32.png',
                              'flags',
                              'index.html',
                              'mstile-150x150.png',
                              'robots.txt',
                              'safari-pinned-tab.svg',
                              'script.js',
                              'site.webmanifest',
                              'style.css'
        ]
        with open("../website/src/data.js") as in_file:
            # Remove the JS bits to keep only the JSON content
            videos_json_content = (in_file.read()[16:-1])
            locations = json.loads(videos_json_content)
        for l in locations:
            expected_prd_files.append("%s.html" % locations[l]["slug"])
            for v in locations[l]["videos"]:
                if v["slug"] not in expected_prd_files:
                    expected_prd_files.append(v["slug"])
        prd_files = os.listdir("../website/prod/")
        self.assertEqual(len(prd_files), len(expected_prd_files))
        for f in expected_prd_files:
            self.assertTrue(f in prd_files)
        #TODO: Confirm the title and h2 of one of the created HTML files have been updated
        # Confirm the aprender/temp folder is not copied to the prd folder
        prd_aprender_files = os.listdir("../website/prod/aprender")
        self.assertFalse("temp" in prd_aprender_files)
        # Confirm the aprender/videos folder doesn't contain unwanted directories
        prd_aprender_videos_files = os.listdir("../website/prod/aprender/videos")
        self.assertFalse("TODO" in prd_aprender_videos_files)
        self.assertFalse("blabla-bla" in prd_aprender_videos_files)

        # Confirm the full HTML pages for /aprender tutorials have been created
        expected_prd_aprender_files = [
            'videos',
            'tutoriales.js',
            'index.html',
            'aprender.js'
        ]
        with open("../website/src/aprender/tutoriales.js") as in_file:
            # Remove the JS bits to keep only the JSON content
            tutoriales_json_content = (in_file.read()[17:-2])
            tutoriales = json.loads(tutoriales_json_content)
        for t in tutoriales:
            expected_prd_aprender_files.append("%s.html" % t["slug"])
        prd_aprender_files = os.listdir("../website/prod/aprender/")
        self.assertEqual(len(prd_aprender_files), len(expected_prd_aprender_files))
        for f in expected_prd_aprender_files:
            self.assertTrue(f in prd_aprender_files)
        #TODO: Confirm the title and h1 of one of the created HTML files have been updated


class TestGenerateSitemap(unittest.TestCase):
    def test_generate_sitemap(self):
        with open("tests/data/sample_locations_final_full.json") as in_file:
            sample_locations = json.load(in_file)
        with open("tests/data/sample_uploaded_videos_dump_full.json") as in_file:
            sample_uploaded_videos = json.load(in_file)
        website.generate_sitemap(website.SITEMAP_FILE, sample_locations, sample_uploaded_videos)
        self.assertTrue(os.path.exists(website.SITEMAP_FILE))
        # Check for the presence of some well-known URLs
        with open(website.SITEMAP_FILE) as in_file:
            sitemap_content = in_file.read()
        self.assertTrue("<loc>https://vallenato.fr</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/mundo-entero</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/buesaco-narino-colombia</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/oye-bonita-buesaco-narino-colombia/KASEblFElVM</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/oye-bonita-buesaco-narino-colombia/yrWZw-lgGbM</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/aprender/</loc>" in sitemap_content)
        self.assertTrue("<loc>https://vallenato.fr/aprender/la-guanena</loc>" in sitemap_content)


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

        # Create a copy of the index.html file that is going to be edited
        (ignore, temp_index_file) = tempfile.mkstemp()
        shutil.copy("../website/src/index.html", temp_index_file)

        website.website(None)

        # Restore the index page
        os.remove("../website/src/index.html")
        shutil.move(temp_index_file, "../website/src/index.html")

        #TODO Assert final script result
        # Delete the temporary file created by the test
        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
