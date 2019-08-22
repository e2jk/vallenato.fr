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

# File that can contain the data downloaded from YouTube
UPLOADED_VIDEOS_DUMP_FILE = "data/uploaded_videos_dump.json"
# File containing the list of videos that have hardcoded locations
LOCATION_SPECIAL_CASES_FILE = "data/location_special_cases.json"
# File containing the already-identified latitude/longitude
GEOLOCATIONS_FILE = "data/geolocations.json"
# Output file used for the website
WEBSITE_DATA_FILE = "../website/data.js"


def get_dumped_uploaded_videos(dump_file):
    uploaded_videos = []
    # Used a previously dumped file if it exists, to bypass the network transactions
    if os.path.exists(dump_file):
        with open(dump_file) as in_file:
            uploaded_videos = json.load(in_file)
    return uploaded_videos

def save_uploaded_videos(uploaded_videos, dump_file):
    with open(dump_file, 'w') as out_file:
        json.dump(uploaded_videos, out_file, sort_keys=True, indent=2)

def get_uploaded_videos(args, dump_file):
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
            save_uploaded_videos(uploaded_videos, dump_file)
    return uploaded_videos

def identify_locations_names(uploaded_videos, location_special_cases_file, dump_file):
    with open(location_special_cases_file) as in_file:
        special_cases = json.load(in_file)
    locations = {}
    incomplete_locations = False
    for vid in uploaded_videos:
        vid["location"] = identify_single_location_name(vid, special_cases)
        if not vid["location"]:
            incomplete_locations = True
        elif vid["location"] not in locations:
            locations[vid["location"]] = {"latitude": None, "longitude": None}
    if incomplete_locations:
        # The script is going to exit, to prevent unnecessary downloading from
        # YouTube again, save the downloaded information regardless of the
        # --dump_uploaded_videos parameter
        save_uploaded_videos(uploaded_videos, dump_file)
        logging.warning("Dumping the list of uploaded videos from YouTube to the '%s' file, so as not to have to download it again after you have edited the '%s' file." % (dump_file, location_special_cases_file))
        logging.critical("Please add the new/missing location to the file '%s'. Exiting..." % location_special_cases_file)
        sys.exit(20)
    logging.info("Found %d different location name." % len(locations))
    return (uploaded_videos, locations)

def identify_single_location_name(vid, special_cases):
    location = None
    if vid["id"] in special_cases:
        location = special_cases[vid["id"]]
        logging.debug("Video %s, location '%s'" % (vid["id"], location))
    else:
        for search_string in (", desde ", ", cerca de "):
            loc_index = vid["title"].find(search_string)
            if loc_index > 0:
                location = vid["title"][loc_index + len(search_string):]
                logging.debug("Video %s, location '%s'" % (vid["id"], location))
                break

    # Each video should now have a location identified. If not, this will end the script.
    if not location:
        logging.critical("No Location found for %s, '%s'" % (vid["id"], vid["title"]))
    return location

def determine_geolocation(locations, geolocations_file):
    logging.debug("Searching geolocation for %d locations..." % len(locations))
    # Load the list of saved geolocations
    with open(geolocations_file) as in_file:
        geolocations = json.load(in_file)
    incomplete_geolocations = 0
    for l in locations:
        if l in geolocations and geolocations[l]["latitude"] and geolocations[l]["longitude"]:
            logging.debug("Geolocation found for %s: lat %f, lon %f" % (l, geolocations[l]["latitude"], geolocations[l]["longitude"]))
            locations[l]["latitude"] = geolocations[l]["latitude"]
            locations[l]["longitude"] = geolocations[l]["longitude"]
        else:
            logging.critical("No geolocation found for %s." % l)
            #TODO: Search and suggest a geolocation
            geolocations[l] = {"latitude": None, "longitude": None}
            incomplete_geolocations += 1

    if incomplete_geolocations > 0:
        #Save the geolocations_file file with the placeholders for the unknown latitude and longitude
        with open(geolocations_file, 'w') as out_file:
            json.dump(geolocations, out_file, sort_keys=True, indent=2)
        logging.critical("Please add the %d new/missing unknown latitude and longitude to the file '%s'. Exiting..." % (incomplete_geolocations, geolocations_file))
        sys.exit(21)

    logging.info("Found geolocation information for the %d locations." % len(locations))
    return locations

def add_videos_to_locations_array(uploaded_videos, locations):
    logging.debug("Adding videos in each location array...")
    for vid in uploaded_videos:
        if not "videos" in locations[vid["location"]]:
            locations[vid["location"]]["videos"] = []
        locations[vid["location"]]["videos"].append(vid)

    return locations

def save_website_data(locations, website_data_file):
    json_content = json.dumps(locations, sort_keys=True, indent=2)
    # Make it JS (and not just JSON) for direct use in the HTML document
    js_content = "var locations = %s;" % json_content
    with open(website_data_file, 'w') as out_file:
        out_file.write(js_content)

def website(args):
    # Retrieve the list of uploaded videos
    uploaded_videos = get_uploaded_videos(args, UPLOADED_VIDEOS_DUMP_FILE)
    logging.info("There are %d uploaded videos." % len(uploaded_videos))

    # Identify each video's location
    (uploaded_videos, locations) = identify_locations_names(uploaded_videos, LOCATION_SPECIAL_CASES_FILE, UPLOADED_VIDEOS_DUMP_FILE)

    # Determine the geolocation of each location
    locations = determine_geolocation(locations, GEOLOCATIONS_FILE)

    # Add the videos in each location array
    locations = add_videos_to_locations_array(uploaded_videos, locations)

    # Generate the JavaScript data file to be used by the website
    save_website_data(locations, WEBSITE_DATA_FILE)
