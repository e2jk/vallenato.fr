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

import logging
import os
import sys
import json

from youtube import HttpError
from youtube import yt_get_authenticated_service
from youtube import yt_get_my_uploads_list
from youtube import yt_list_my_uploaded_videos

# File containing the list of videos that have hardcoded locations
LOCATION_SPECIAL_CASES_FILE = "data/location_special_cases.json"

def get_dumped_uploaded_videos(dump_file):
    uploaded_videos = []
    # Used a previously dumped file if it exists, to bypass the network transactions
    if os.path.exists(dump_file):
        with open(dump_file) as in_file:
            uploaded_videos = json.load(in_file)
    return uploaded_videos

def get_uploaded_videos(args):
    dump_file = "uploaded_videos_dump.txt"
    uploaded_videos = get_dumped_uploaded_videos(dump_file)
    if not uploaded_videos:
        youtube = yt_get_authenticated_service(args)
        # Get the list of videos uploaded to YouTube
        try:
            uploads_playlist_id = yt_get_my_uploads_list(youtube)
            if uploads_playlist_id:
                uploaded_videos = yt_list_my_uploaded_videos(uploads_playlist_id, youtube)
                logging.debug("Uploaded videos: %s" % uploaded_videos)
            else:
                logging.info('There is no uploaded videos playlist for this user.')
        except HttpError as e:
            logging.debug('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
            logging.critical("Exiting...")
            sys.exit(19)
        if args.dump_uploaded_videos:
            with open(dump_file, 'w') as out_file:
                json.dump(uploaded_videos, out_file, sort_keys=True, indent=2)
    return uploaded_videos

def identify_locations_names(uploaded_videos, location_special_cases_file):
    with open(location_special_cases_file) as in_file:
        special_cases = json.load(in_file)
    incomplete_locations = False
    for vid in uploaded_videos:
        vid["location"] = identify_single_location_name(vid, special_cases)
        if not vid["location"]:
            incomplete_locations = True
    if incomplete_locations:
        logging.critical("Please add the new/missing location to the file '%s'. Exiting..." % location_special_cases_file)
        sys.exit(20)
    return uploaded_videos

def identify_single_location_name(vid, special_cases):
    location = None
    if vid["id"] in special_cases:
        location = special_cases[vid["id"]]
    else:
        for search_string in (", desde ", ", cerca de "):
            loc_index = vid["title"].find(search_string)
            if loc_index > 0:
                location = vid["title"][loc_index + len(search_string):]
                break
    # Each video should now have a location identified. If not, this will end the script.
    if not location:
        logging.critical("No Location found for %s, '%s'" % (vid["id"], vid["title"]))
    return location

def website(args):
    # Retrieve the list of uploaded videos
    uploaded_videos = get_uploaded_videos(args)
    logging.info("There are %d uploaded videos." % len(uploaded_videos))

    # Identify each video's location
    uploaded_videos = identify_locations_names(uploaded_videos, LOCATION_SPECIAL_CASES_FILE)

    # Determine the geolocation of each location
    #TODO

    # Create arrays per location
    #TODO

    # Generate the JavaScript files to be used by the website
    #TODO
