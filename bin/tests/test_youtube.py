#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && rm -rf ../html_dev/coverage && coverage html --directory=../html_dev/coverage --title="Code test coverage for vallenato.fr"

import unittest
import sys
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call

sys.path.append('.')
target = __import__("vallenato_fr")
youtube = __import__("youtube")


class TestYtGetAuthenticatedService(unittest.TestCase):
    @patch("youtube.build")
    @patch("youtube.run_flow")
    @patch("youtube.Storage")
    @patch("youtube.flow_from_clientsecrets")
    def test_yt_get_authenticated_service(self, yt_ffc, yt_S, yt_rf, yt_b):
        args = target.parse_args(['--website'])
        yt = youtube.yt_get_authenticated_service(args)
        expected_yt_ffc = [call('client_secret.json', message='\nWARNING: Please configure OAuth 2.0\n\nTo make this sample run you will need to populate the client_secrets.json file\nfound at:\n   /home/emilien/devel/vallenato.fr/bin/client_secret.json\nwith information from the APIs Console\nhttps://console.developers.google.com\n\nFor more information about the client_secrets.json file format, please visit:\nhttps://developers.google.com/api-client-library/python/guide/aaa_client_secrets\n', scope=['https://www.googleapis.com/auth/youtube.readonly'])]
        self.assertTrue(expected_yt_ffc in yt_ffc.mock_calls)
        self.assertTrue(call('vallenato.fr-oauth2.json') in yt_S.mock_calls)
        self.assertEqual([call(yt_ffc(), yt_S(), args)], yt_rf.mock_calls)
        expected_yt_b = [call('youtube', 'v3', cache_discovery=False, credentials=yt_rf())]
        self.assertTrue(expected_yt_b in yt_b.mock_calls)


class TestYtGetMyUploadsList(unittest.TestCase):
    def test_yt_get_my_uploads_list(self):
        uploads_playlist_id = youtube.yt_get_my_uploads_list(None)
        self.assertEqual(uploads_playlist_id, "UU_8R235jg1ld6MCMOzz2khQ")


# class TestYtListMyUploadedVideos(unittest.TestCase):
#     def test_yt_list_my_uploaded_videos(self):
#         yt = MagicMock()
#         uploaded_videos = youtube.yt_list_my_uploaded_videos("UU_8R235jg1ld6MCMOzz2khQ", yt)


if __name__ == '__main__':
    unittest.main()
