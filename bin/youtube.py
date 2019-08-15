#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of Vallenato.fr.
#
#    Vallenato.fr is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Vallenato.fr is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Vallenato.fr.  If not, see <http://www.gnu.org/licenses/>.

# Adapted from:
#   https://github.com/youtube/api-samples/blob/master/python/my_uploads.py
#   https://github.com/youtube/api-samples/blob/master/python/upload_video.py

import httplib2
import os
import logging
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow




# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'client_secret.json'

# This OAuth 2.0 access scope allows an application to view videos and playlists
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

# Authorize the request and store authorization credentials.
def yt_get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=SCOPES, message=MISSING_CLIENT_SECRETS_MESSAGE)
    storage = Storage("vallenato.fr-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials, cache_discovery=False)

def yt_get_my_uploads_list(youtube):
    return "UU_8R235jg1ld6MCMOzz2khQ"
    # # Retrieve the contentDetails part of the channel resource for the
    # # authenticated user's channel.
    # channels_response = youtube.channels().list(
    #     mine=True,
    #     part='contentDetails'
    # ).execute()
    #
    # for channel in channels_response['items']:
    #     # From the API response, extract the playlist ID that identifies the list
    #     # of videos uploaded to the authenticated user's channel.
    #     return channel['contentDetails']['relatedPlaylists']['uploads']
    # return None

def yt_list_my_uploaded_videos(uploads_playlist_id, youtube):
    uploaded_videos = []
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part='contentDetails'
    )

    logging.debug('Videos in list %s' % uploads_playlist_id)
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        videoIds = ",".join(playlist_item['contentDetails']['videoId'] for playlist_item in playlistitems_list_response['items'])

        # To get the videos' tags, we need to do an extra query
        videos_list_request = youtube.videos().list(
            id=videoIds,
            part='snippet,status'
        )

        while videos_list_request:
            videos_list_response = videos_list_request.execute()

            for video in videos_list_response['items']:
                # Only keep Public videos not tagged as "no-website" or "Tutorial"
                if (video['status']['privacyStatus'] != "public" or
                   "no-website" in video['snippet']['tags'] or
                   "Tutorial" in video['snippet']['tags']):
                    continue
                vid = {}
                vid["id"] = video['id']
                vid["title"] = video['snippet']['title']
                vid["description"] = video['snippet']['description']
                try:
                    vid["tags"] = video['snippet']['tags']
                except KeyError:
                    vid["tags"] = []
                vid["publishedAt"] = video['snippet']['publishedAt']
                vid["thumbnail"] = video['snippet']['thumbnails']['default']

                uploaded_videos.append(vid)
                logging.debug(vid)
            videos_list_request = youtube.videos().list_next(videos_list_request, videos_list_response)

        playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
    return uploaded_videos
