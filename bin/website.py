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
import shutil
from slugify import slugify
import sitemap.generator as generator

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
WEBSITE_DATA_FILE = "../website/src/data.js"
# Sitemap file
SITEMAP_FILE = "../website/prod/sitemap.xml"
# Version of the external libraries
LEAFLET_VERSION = "1.5.1"
BOOTSTRAP_VERSION = "4.3.1"
JQUERY_VERSION = "3.3.1"


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

def determine_videos_slug(uploaded_videos):
    logging.debug("Determining each video's slug...")
    for vid in uploaded_videos:
        vid["slug"] = slugify(vid["title"]).replace("-desde-", "-")
    return uploaded_videos

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
        # Create a slug for each video (to be used for the website URLs)
        uploaded_videos = determine_videos_slug(uploaded_videos)
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

def determine_locations_slug(locations):
    logging.debug("Determining each location's slug...")
    for loc in locations:
        locations[loc]["slug"] = slugify(loc)
    return locations

def save_website_data(locations, website_data_file):
    json_content = json.dumps(locations, sort_keys=True, indent=2)
    # Make it JS (and not just JSON) for direct use in the HTML document
    js_content = "var locations = %s;" % json_content
    with open(website_data_file, 'w') as out_file:
        out_file.write(js_content)

def ignored_files_in_prod(adir, filenames):
    ignored_files = []
    if "../website/src" == adir:
        ignored_files = [
            'bootstrap-%s-dist' % BOOTSTRAP_VERSION,
            'jquery-%s.slim.min.js' % JQUERY_VERSION,
            'leaflet'
        ]
    if "../website/src/aprender" == adir:
        ignored_files = [
            'temp',
            'videos'
        ]
    return [filename for filename in filenames if filename in ignored_files]

def generate_website():
    input_src_folder = "../website/src"
    output_prod_folder = "../website/prod"

    # Delete the previous production output folder (if existing)
    if os.path.exists(output_prod_folder):
        shutil.rmtree(output_prod_folder)

    # Update the values accordingly for prod
    # Main difference between development (src) and production websites:
    # - src contains a full copy of the leaflet, Bootstrap and jQuery libraries
    # - prod uses CDNs

    # Copy src to prod folder, ignoring the files and folder replaced by CDNs in prod
    # The videos are also not copied, as we're going to hard-link them
    shutil.copytree(input_src_folder, output_prod_folder, ignore=ignored_files_in_prod)

    # Create hard links for the videos in the prod folder
    # (hard links can only be created for files, need to recreate the folder structure)
    os.mkdir("%s/aprender/videos" % output_prod_folder)
    for d in os.listdir("%s/aprender/videos" % input_src_folder):
        if d not in ["TODO", "blabla-bla"]:
            # Create a folder for that tutorial's video files
            #TODO: copy folder without content in order to keep the original folder's
            # creation date, in order to not confuse the rsync upload process
            os.mkdir("%s/aprender/videos/%s" % (output_prod_folder, d))
            for f in os.listdir("%s/aprender/videos/%s" % (input_src_folder, d)):
                # Create a hard link to the video file
                os.link("%s/aprender/videos/%s/%s" % (input_src_folder, d, f),
                        "%s/aprender/videos/%s/%s" % (output_prod_folder, d, f))

    # Update links to leaflet (CDN)
    # Read the prod files
    with open("%s/index.html" % output_prod_folder, 'r') as file :
        index_data = file.read()
    with open("%s/aprender/index.html" % output_prod_folder, 'r') as file :
        index_aprender_data = file.read()
    # Replace the target strings
    # Leaflet
    index_data = index_data.replace(
        '<link rel="stylesheet" href="leaflet/%s/leaflet.css">' % LEAFLET_VERSION,
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@%s/dist/leaflet.css"\n        integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="\n        crossorigin=""/>' % LEAFLET_VERSION)
    index_data = index_data.replace(
        '<script type = "text/javascript" src="leaflet/%s/leaflet.js"></script>' % LEAFLET_VERSION,
        '<script src="https://unpkg.com/leaflet@%s/dist/leaflet.js"\n        integrity="sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og=="\n        crossorigin="">\n    </script>' % LEAFLET_VERSION)
    # Bootstrap
    index_data = index_data.replace(
        '<link rel="stylesheet" href="bootstrap-%s-dist/css/bootstrap.min.css">' % BOOTSTRAP_VERSION,
        '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css"\n        integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"\n        crossorigin="anonymous">' % BOOTSTRAP_VERSION)
    index_data = index_data.replace(
        '<script src="bootstrap-%s-dist/js/bootstrap.min.js"></script>' % BOOTSTRAP_VERSION,
        '<script src="https://stackpath.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js"\n        integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"\n        crossorigin="anonymous"></script>' % BOOTSTRAP_VERSION)
    index_aprender_data = index_aprender_data.replace(
        '<link rel="stylesheet" href="../bootstrap-%s-dist/css/bootstrap.min.css">' % BOOTSTRAP_VERSION,
        '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css"\n        integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"\n        crossorigin="anonymous">' % BOOTSTRAP_VERSION)
    index_aprender_data = index_aprender_data.replace(
        '<script src="../bootstrap-%s-dist/js/bootstrap.min.js"></script>' % BOOTSTRAP_VERSION,
        '<script src="https://stackpath.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js"\n        integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"\n        crossorigin="anonymous"></script>' % BOOTSTRAP_VERSION)
    # jQuery (for Bootstrap)
    index_data = index_data.replace(
        '<script src="jquery-%s.slim.min.js"></script>' % JQUERY_VERSION,
        '<script src="https://code.jquery.com/jquery-%s.slim.min.js"\n        integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"\n        crossorigin="anonymous"></script>' % JQUERY_VERSION)
    index_aprender_data = index_aprender_data.replace(
        '<script src="../jquery-%s.slim.min.js"></script>' % JQUERY_VERSION,
        '<script src="https://code.jquery.com/jquery-%s.slim.min.js"\n        integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"\n        crossorigin="anonymous"></script>' % JQUERY_VERSION)

    # Save edited prod files
    with open("%s/index.html" % output_prod_folder, 'w') as file:
        file.write(index_data)
    with open("%s/aprender/index.html" % output_prod_folder, 'w') as file:
        file.write(index_aprender_data)

def generate_sitemap(sitemap_file, locations, uploaded_videos):
    base_url = "https://vallenato.fr"
    sitemap = generator.Sitemap()

    # vallenato.fr index
    sitemap.add(base_url,
                # Timestamp of the most recently uploaded video
                lastmod=uploaded_videos[0]["publishedAt"][:10],
                changefreq="monthly",
                priority="1.0")

    # Locations and individual videos
    sitemap.add("%s/mundo-entero" % base_url,
                # Timestamp of the most recently uploaded video
                lastmod=uploaded_videos[0]["publishedAt"][:10],
                changefreq="monthly",
                priority="0.6")
    for l in locations:
        # Locations
        sitemap.add("%s/%s" % (base_url, locations[l]["slug"]),
                    # Timestamp of the most recently uploaded video at that location
                    lastmod=locations[l]["videos"][0]["publishedAt"][:10],
                    changefreq="yearly",
                    priority="0.5")
        for v in locations[l]["videos"]:
            # Individual videos
            sitemap.add("%s/%s/%s" % (base_url, v["slug"], v["id"]),
                        # Timestamp of that video
                        lastmod=v["publishedAt"][:10],
                        changefreq="yearly",
                        priority="0.5")

    # Aprender index
    sitemap.add("%s/aprender/" % base_url,
                changefreq="monthly",
                priority="1.0")

    # Aprender: individual tutorials
    with open("../website/src/aprender/tutoriales.js") as in_file:
        # Remove the JS bits to keep only the JSON content
        tutoriales_json_content = (in_file.read()[17:-2])
        tutoriales = json.loads(tutoriales_json_content)
    for t in tutoriales:
        tuto_url = "%s/aprender/%s" % (base_url, t["slug"])
        sitemap.add(tuto_url,
                    changefreq="yearly",
                    priority="0.5")

    sitemap_xml = sitemap.generate()

    # Prettify the XML "by hand"
    sitemap_xml = sitemap_xml.replace("<url>", "  <url>")
    sitemap_xml = sitemap_xml.replace("</url>", "  </url>")
    sitemap_xml = sitemap_xml.replace("<loc>", "    <loc>")
    sitemap_xml = sitemap_xml.replace("<lastmod>", "    <lastmod>")
    sitemap_xml = sitemap_xml.replace("<changefreq>", "    <changefreq>")
    sitemap_xml = sitemap_xml.replace("<priority>", "    <priority>")

    with open(sitemap_file, 'w') as file:
        file.write(sitemap_xml)

def website(args):
    # Retrieve the list of uploaded videos
    uploaded_videos = get_uploaded_videos(args, UPLOADED_VIDEOS_DUMP_FILE)
    logging.info("There are %d uploaded videos." % len(uploaded_videos))

    # Identify each video's location
    (uploaded_videos, locations) = identify_locations_names(uploaded_videos, LOCATION_SPECIAL_CASES_FILE, UPLOADED_VIDEOS_DUMP_FILE)

    # Determine the geolocation of each location
    locations = determine_geolocation(locations, GEOLOCATIONS_FILE)

    # Create a slug for each location (to be used for the website URLs)
    locations = determine_locations_slug(locations)

    # Add the videos in each location array
    locations = add_videos_to_locations_array(uploaded_videos, locations)

    # Generate the JavaScript data file to be used by the website
    save_website_data(locations, WEBSITE_DATA_FILE)

    # Generate the development and production website files
    generate_website()

    # Generate the Sitemap
    generate_sitemap(SITEMAP_FILE, locations, uploaded_videos)
