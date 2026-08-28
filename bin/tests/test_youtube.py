# Running the tests (with coverage): $ sh test.sh
# Running just this file:                 $ python3 -m pytest tests/test_youtube.py

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

sys.path.append(".")
target = __import__("vallenato_fr")
youtube = __import__("youtube")


class TestYtGetAuthenticatedService(unittest.TestCase):
    @patch("youtube.build")
    @patch("youtube.run_flow")
    @patch("youtube.Storage")
    @patch("youtube.flow_from_clientsecrets")
    def test_yt_get_authenticated_service(self, yt_ffc, yt_S, yt_rf, yt_b):
        args = target.parse_args(["--website"])
        youtube.yt_get_authenticated_service(args)
        # local_file_path = "/home/emilien/devel/vallenato.fr/bin"
        local_file_path = os.getcwd()
        expected_yt_ffc = [
            call(
                "client_secret.json",
                message=f"\nWARNING: Please configure OAuth 2.0\n\nTo make this sample run you will need to populate the client_secrets.json file\nfound at:\n   {local_file_path}/client_secret.json\nwith information from the APIs Console\nhttps://console.developers.google.com\n\nFor more information about the client_secrets.json file format, please visit:\nhttps://developers.google.com/api-client-library/python/guide/aaa_client_secrets\n",
                scope=["https://www.googleapis.com/auth/youtube.readonly"],
            )
        ]
        self.assertTrue(expected_yt_ffc in yt_ffc.mock_calls)
        self.assertTrue(call("vallenato.fr-oauth2.json") in yt_S.mock_calls)
        self.assertEqual([call(yt_ffc(), yt_S(), args)], yt_rf.mock_calls)
        expected_yt_b = [
            call("youtube", "v3", cache_discovery=False, credentials=yt_rf())
        ]
        self.assertTrue(expected_yt_b in yt_b.mock_calls)


class TestYtGetMyUploadsList(unittest.TestCase):
    def test_yt_get_my_uploads_list(self):
        uploads_playlist_id = youtube.yt_get_my_uploads_list(None)
        self.assertEqual(uploads_playlist_id, "UU_8R235jg1ld6MCMOzz2khQ")


class TestYtListMyUploadedVideos(unittest.TestCase):
    def test_yt_list_my_uploaded_videos(self):
        yt = MagicMock()

        def make_video(vid, privacy="public", tags="__absent__"):
            snippet = {
                "title": f"Title {vid}",
                "description": f"Description {vid}",
                "publishedAt": "2020-01-01T00:00:00Z",
                "thumbnails": {
                    "default": {
                        "url": f"https://i.ytimg.com/vi/{vid}/default.jpg",
                        "width": 120,
                        "height": 90,
                    },
                    "medium": {
                        "url": f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
                        "width": 320,
                        "height": 180,
                    },
                },
            }
            if tags != "__absent__":
                snippet["tags"] = tags
            return {"id": vid, "snippet": snippet, "status": {"privacyStatus": privacy}}

        # Page 1 of videos.list(): a video with no 'tags' key at all (falls
        # back to []), one tagged "no-website", one tagged "Tutorial" — the
        # latter two should be filtered out.
        video_no_tags = make_video("vidA")
        video_no_website = make_video("vidB", tags=["Acordeón", "no-website"])
        video_tutorial = make_video("vidC", tags=["Tutorial"])
        # Page 2: a non-public video (filtered out) and a normal public one.
        video_private = make_video("vidD", privacy="private")
        video_normal = make_video("vidE", tags=["Acordeón", "Vallenato"])

        playlistitems_response = {
            "items": [
                {"contentDetails": {"videoId": "vidA"}},
                {"contentDetails": {"videoId": "vidB"}},
                {"contentDetails": {"videoId": "vidC"}},
                {"contentDetails": {"videoId": "vidD"}},
                {"contentDetails": {"videoId": "vidE"}},
            ]
        }
        videos_response_page1 = {
            "items": [video_no_tags, video_no_website, video_tutorial]
        }
        videos_response_page2 = {"items": [video_private, video_normal]}

        playlistitems_request = MagicMock()
        playlistitems_request.execute.return_value = playlistitems_response
        yt.playlistItems.return_value.list.return_value = playlistitems_request
        # Only one page of playlist items
        yt.playlistItems.return_value.list_next.side_effect = [None]

        videos_request_page1 = MagicMock()
        videos_request_page1.execute.return_value = videos_response_page1
        videos_request_page2 = MagicMock()
        videos_request_page2.execute.return_value = videos_response_page2
        yt.videos.return_value.list.return_value = videos_request_page1
        yt.videos.return_value.list_next.side_effect = [videos_request_page2, None]

        uploaded_videos = youtube.yt_list_my_uploaded_videos(
            "UU_8R235jg1ld6MCMOzz2khQ", yt
        )

        self.assertEqual([v["id"] for v in uploaded_videos], ["vidA", "vidE"])
        self.assertEqual(
            uploaded_videos[0],
            {
                "id": "vidA",
                "title": "Title vidA",
                "description": "Description vidA",
                "tags": [],
                "publishedAt": "2020-01-01T00:00:00Z",
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi/vidA/mqdefault.jpg",
                    "width": 320,
                    "height": 180,
                },
            },
        )
        self.assertEqual(
            uploaded_videos[1],
            {
                "id": "vidE",
                "title": "Title vidE",
                "description": "Description vidE",
                "tags": ["Acordeón", "Vallenato"],
                "publishedAt": "2020-01-01T00:00:00Z",
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi/vidE/mqdefault.jpg",
                    "width": 320,
                    "height": 180,
                },
            },
        )

        yt.playlistItems.return_value.list.assert_called_once_with(
            playlistId="UU_8R235jg1ld6MCMOzz2khQ", part="contentDetails"
        )


if __name__ == "__main__":
    unittest.main()
