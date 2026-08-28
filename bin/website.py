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

import datetime
import json
import logging
import os
import re
import shutil
import sys

from sitemap import generator
from slugify import slugify

from youtube import (
    HttpError,
    yt_get_authenticated_service,
    yt_get_my_uploads_list,
    yt_list_my_uploaded_videos,
)

logger = logging.getLogger(__name__)

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
LEAFLET_VERSION = "1.9.4"
BOOTSTRAP_VERSION = "4.6.2"
JQUERY_VERSION = "3.7.1"
BOOTSTRAP_TOGGLE_VERSION = "3.6.1"


def get_dumped_uploaded_videos(dump_file):
    uploaded_videos = []
    # Used a previously dumped file if it exists, to bypass the network transactions
    if os.path.exists(dump_file):
        with open(dump_file) as in_file:
            uploaded_videos = json.load(in_file)
    return uploaded_videos


def save_uploaded_videos(uploaded_videos, dump_file):
    with open(dump_file, "w") as out_file:
        json.dump(uploaded_videos, out_file, sort_keys=True, indent=2)


def determine_videos_slug(uploaded_videos):
    logger.debug("Determining each video's slug...")
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
                uploaded_videos = yt_list_my_uploaded_videos(
                    uploads_playlist_id, youtube
                )
                logger.debug(f"Uploaded videos: {uploaded_videos}")
            else:
                logger.info("There is no uploaded videos playlist for this user.")
        except HttpError as e:
            logger.debug(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
            logger.critical("Exiting...")
            sys.exit(19)
        # Create a slug for each video (to be used for the website URLs)
        uploaded_videos = determine_videos_slug(uploaded_videos)
        if args.dump_uploaded_videos:
            save_uploaded_videos(uploaded_videos, dump_file)
    return uploaded_videos


def identify_locations_names(uploaded_videos, location_special_cases_file, dump_file):
    logger.debug("Identify each video's location name")
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
        logger.warning(
            f"Dumping the list of uploaded videos from YouTube to the '{dump_file}' file, so as not to have to download it again after you have edited the '{location_special_cases_file}' file."
        )
        save_uploaded_videos(uploaded_videos, dump_file)
        logger.critical(
            f"Please add the new/missing location to the file '{location_special_cases_file}'. Exiting..."
        )
        sys.exit(20)
    logger.info(f"Found {len(locations)} different location name.")
    return (uploaded_videos, locations)


def identify_single_location_name(vid, special_cases):
    location = None
    if vid["id"] in special_cases:
        location = special_cases[vid["id"]]
        logger.debug("Video {}, location '{}'".format(vid["id"], location))
    else:
        for search_string in (", desde ", ", cerca de "):
            loc_index = vid["title"].find(search_string)
            if loc_index > 0:
                location = vid["title"][loc_index + len(search_string) :]
                logger.debug("Video {}, location '{}'".format(vid["id"], location))
                break

    # Each video should now have a location identified. If not, this will end the script.
    if not location:
        logger.critical(
            "No Location found for {}, '{}'".format(vid["id"], vid["title"])
        )
    return location


def determine_geolocation(locations, geolocations_file):
    logger.debug(f"Searching geolocation for {len(locations)} locations...")
    # Load the list of saved geolocations
    with open(geolocations_file) as in_file:
        geolocations = json.load(in_file)
    incomplete_geolocations = 0
    for l in locations:
        if (
            l in geolocations
            and geolocations[l]["latitude"]
            and geolocations[l]["longitude"]
        ):
            logger.debug(
                "Geolocation found for {}: lat {:f}, lon {:f}".format(
                    l, geolocations[l]["latitude"], geolocations[l]["longitude"]
                )
            )
            locations[l]["latitude"] = geolocations[l]["latitude"]
            locations[l]["longitude"] = geolocations[l]["longitude"]
        else:
            logger.critical(f"No geolocation found for {l}.")
            # TODO: Search and suggest a geolocation
            geolocations[l] = {"latitude": None, "longitude": None}
            incomplete_geolocations += 1

    if incomplete_geolocations > 0:
        # Save the geolocations_file file with the placeholders for the unknown latitude and longitude
        with open(geolocations_file, "w") as out_file:
            json.dump(geolocations, out_file, sort_keys=True, indent=2)
        logger.critical(
            f"Please add the {incomplete_geolocations} new/missing unknown latitude and longitude to the file '{geolocations_file}'. Exiting..."
        )
        sys.exit(21)

    logger.info(f"Found geolocation information for the {len(locations)} locations.")
    return locations


def add_videos_to_locations_array(uploaded_videos, locations):
    logger.debug("Adding videos in each location array...")
    for vid in uploaded_videos:
        if not "videos" in locations[vid["location"]]:
            locations[vid["location"]]["videos"] = []
        locations[vid["location"]]["videos"].append(vid)
    return locations


def determine_locations_slug(locations):
    logger.debug("Determining each location's slug...")
    for loc in locations:
        locations[loc]["slug"] = slugify(loc)
    return locations


def save_website_data(locations, website_data_file):
    logger.debug("Save the updated dynamic data")
    json_content = json.dumps(locations, sort_keys=True, indent=2)
    # Make it JS (and not just JSON) for direct use in the HTML document
    js_content = f"var locations = {json_content};"
    with open(website_data_file, "w") as out_file:
        out_file.write(js_content)


def load_locations_from_website_data_file(website_data_file):
    # Used by --no-fetch: rebuild the website from what's already committed
    # to website/src/data.js instead of hitting the YouTube API, e.g. to
    # build the production Docker image without live OAuth credentials.
    logger.debug(f"Loading existing locations from {website_data_file} (--no-fetch)")
    with open(website_data_file) as in_file:
        # Remove the JS bits to keep only the JSON content
        return json.loads(in_file.read()[16:-1])


def flatten_videos_from_locations(locations):
    uploaded_videos = []
    for location in locations.values():
        uploaded_videos.extend(location["videos"])
    uploaded_videos.sort(key=lambda v: v["publishedAt"], reverse=True)
    return uploaded_videos


def ignored_files_in_prod(adir, filenames):
    ignored_files = []
    if "../website/src" == adir:
        ignored_files = [
            f"bootstrap-{BOOTSTRAP_VERSION}-dist",
            f"bootstrap4-toggle-{BOOTSTRAP_TOGGLE_VERSION}",
            f"jquery-{JQUERY_VERSION}.slim.min.js",
            "leaflet",
        ]
    if "../website/src/aprender" == adir:
        ignored_files = ["temp", "videos"]
    return [filename for filename in filenames if filename in ignored_files]


def get_stats(locations, uploaded_videos):
    num_videos = len(uploaded_videos)

    songs = []
    skipped_titles = ["Vallenato at Epic", "La Guaneña navideña"]
    for v in uploaded_videos:
        song = v["title"].split(",")[0]
        if song not in songs and song not in skipped_titles:
            songs.append(song)
    num_songs = len(songs)

    num_places = len(locations)

    countries = []
    for l in locations:
        country = l.split(",")[-1]
        if country not in countries:
            countries.append(country)
    num_countries = len(countries)

    navidad_2017 = datetime.date(2017, 12, 25)
    today = datetime.date.today()
    years = today.year - navidad_2017.year
    if today.month == 12:  # December
        duration_since_navidad_2017 = f"{years} años"
    elif today.month == 1:  # January
        duration_since_navidad_2017 = f"{years - 1} años"
    else:
        duration_since_navidad_2017 = f"{years - 1} años y {today.month} meses"

    stats = f"El Vallenatero Francés les presenta {num_videos} videos de {num_songs} canciones tocadas en {num_places} lugares de {num_countries} paises. El empezo a aprender el Acordeón Vallenato en la Navidad 2017 (hace mas o menos {duration_since_navidad_2017})."

    return stats


def generate_website(locations, uploaded_videos):
    logger.debug("Generate the production website files")
    input_src_folder = "../website/src"
    output_prod_folder = "../website/prod"
    # The 2 index files in / and /aprender,  404
    num_html_pages_created = 3

    # Delete the previous production output folder (if existing)
    if os.path.exists(output_prod_folder):
        shutil.rmtree(output_prod_folder)

    # Update statistics
    stats = get_stats(locations, uploaded_videos)
    index_src_file = f"{input_src_folder}/index.html"
    with open(index_src_file, "r") as file:
        index_data = file.read()
    index_data = re.sub(
        '<div id="stats">.*</div>', f'<div id="stats">{stats}</div>', index_data
    )
    with open(index_src_file, "w") as file:
        file.write(index_data)

    # Update the values accordingly for prod
    # Main difference between development (src) and production websites:
    # - src contains a full copy of the leaflet, Bootstrap and jQuery libraries
    # - prod uses CDNs

    # Copy src to prod folder, ignoring the files and folder replaced by CDNs in prod
    # The videos are also not copied, as we're going to hard-link them
    shutil.copytree(input_src_folder, output_prod_folder, ignore=ignored_files_in_prod)

    # Create hard links for the videos in the prod folder
    # (hard links can only be created for files, need to recreate the folder structure)
    os.mkdir(f"{output_prod_folder}/aprender/videos")
    # website/src/aprender/videos/ is gitignored (and .dockerignore'd) - it
    # only exists locally once a tutorial's video files have been downloaded
    # via --aprender. A fresh checkout (or a Docker build context, which
    # never sends it in) has no such directory yet - nothing to hard-link.
    videos_src_dir = f"{input_src_folder}/aprender/videos"
    for d in os.listdir(videos_src_dir) if os.path.isdir(videos_src_dir) else []:
        if d not in ["TODO", "blabla-bla"]:
            # Create a folder for that tutorial's video files
            # TODO: copy folder without content in order to keep the original folder's
            # creation date, in order to not confuse the rsync upload process
            os.mkdir(f"{output_prod_folder}/aprender/videos/{d}")
            for f in os.listdir(f"{input_src_folder}/aprender/videos/{d}"):
                # Create a hard link to the video file
                os.link(
                    f"{input_src_folder}/aprender/videos/{d}/{f}",
                    f"{output_prod_folder}/aprender/videos/{d}/{f}",
                )

    # Update links to leaflet (CDN)
    # Read the prod files
    with open(f"{output_prod_folder}/index.html", "r") as file:
        index_data = file.read()
    with open(f"{output_prod_folder}/404.html", "r") as file:
        page404_data = file.read()
    with open(f"{output_prod_folder}/aprender/index.html", "r") as file:
        index_aprender_data = file.read()
    # Replace the target strings
    # Leaflet
    index_data = index_data.replace(
        f'<link rel="stylesheet" href="leaflet/{LEAFLET_VERSION}/leaflet.css">',
        f'<link rel="stylesheet" href="https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.css"\n        integrity="sha512-Zcn6bjR/8RZbLEpLIeOwNtzREBAJnUKESxces60Mpoj+2okopSAcSUIUOseddDm0cxnGQzxIR7vJgsLZbdLE3w=="\n        crossorigin=""/>',
    )
    index_data = index_data.replace(
        f'<script type = "text/javascript" src="leaflet/{LEAFLET_VERSION}/leaflet.js"></script>',
        f'<script src="https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.js"\n        integrity="sha512-BwHfrr4c9kmRkLw6iXFdzcdWV/PGkVgiIyIWLLlTSXzWQzxuSg4DiQUCpauz/EWjgk5TYQqX/kvn9pG1NpYfqg=="\n        crossorigin="">\n    </script>',
    )
    # Bootstrap
    index_data = index_data.replace(
        f'<link rel="stylesheet" href="bootstrap-{BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css">',
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"\n        integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N"\n        crossorigin="anonymous">',
    )
    index_data = index_data.replace(
        f'<script src="bootstrap-{BOOTSTRAP_VERSION}-dist/js/bootstrap.min.js"></script>',
        f'<script src="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.min.js"\n        integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+"\n        crossorigin="anonymous"></script>',
    )
    page404_data = page404_data.replace(
        f'<link rel="stylesheet" href="bootstrap-{BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css">',
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"\n        integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N"\n        crossorigin="anonymous">',
    )
    page404_data = page404_data.replace(
        f'<script src="bootstrap-{BOOTSTRAP_VERSION}-dist/js/bootstrap.min.js"></script>',
        f'<script src="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.min.js"\n        integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+"\n        crossorigin="anonymous"></script>',
    )
    index_aprender_data = index_aprender_data.replace(
        f'<link rel="stylesheet" href="../bootstrap-{BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css">',
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"\n        integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N"\n        crossorigin="anonymous">',
    )
    index_aprender_data = index_aprender_data.replace(
        f'<script src="../bootstrap-{BOOTSTRAP_VERSION}-dist/js/bootstrap.min.js"></script>',
        f'<script src="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.min.js"\n        integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+"\n        crossorigin="anonymous"></script>',
    )
    # jQuery (for Bootstrap)
    index_data = index_data.replace(
        f'<script src="jquery-{JQUERY_VERSION}.slim.min.js"></script>',
        f'<script src="https://code.jquery.com/jquery-{JQUERY_VERSION}.slim.min.js"\n        integrity="sha384-5AkRS45j4ukf+JbWAfHL8P4onPA9p0KwwP7pUdjSQA3ss9edbJUJc/XcYAiheSSz"\n        crossorigin="anonymous"></script>',
    )
    page404_data = page404_data.replace(
        f'<script src="jquery-{JQUERY_VERSION}.slim.min.js"></script>',
        f'<script src="https://code.jquery.com/jquery-{JQUERY_VERSION}.slim.min.js"\n        integrity="sha384-5AkRS45j4ukf+JbWAfHL8P4onPA9p0KwwP7pUdjSQA3ss9edbJUJc/XcYAiheSSz"\n        crossorigin="anonymous"></script>',
    )
    index_aprender_data = index_aprender_data.replace(
        f'<script src="../jquery-{JQUERY_VERSION}.slim.min.js"></script>',
        f'<script src="https://code.jquery.com/jquery-{JQUERY_VERSION}.slim.min.js"\n        integrity="sha384-5AkRS45j4ukf+JbWAfHL8P4onPA9p0KwwP7pUdjSQA3ss9edbJUJc/XcYAiheSSz"\n        crossorigin="anonymous"></script>',
    )
    # Bootstrap-toggle
    index_aprender_data = index_aprender_data.replace(
        f'<link rel="stylesheet" href="../bootstrap4-toggle-{BOOTSTRAP_TOGGLE_VERSION}/css/bootstrap4-toggle.min.css">',
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@{BOOTSTRAP_TOGGLE_VERSION}/css/bootstrap4-toggle.min.css"\n        integrity="sha384-yakM86Cz9KJ6CeFVbopALOEQGGvyBFdmA4oHMiYuHcd9L59pLkCEFSlr6M9m434E"\n        crossorigin="anonymous">',
    )
    index_aprender_data = index_aprender_data.replace(
        f'<script src="../bootstrap4-toggle-{BOOTSTRAP_TOGGLE_VERSION}/js/bootstrap4-toggle.min.js"></script>',
        f'<script src="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@{BOOTSTRAP_TOGGLE_VERSION}/js/bootstrap4-toggle.min.js"\n        integrity="sha384-Q9RsZ4GMzjlu4FFkJw4No9Hvvm958HqHmXI9nqo5Np2dA/uOVBvKVxAvlBQrDhk4"\n        crossorigin="anonymous"></script>',
    )
    # Copyright year in the pages' footer
    a = '<span class="text-muted">&copy; YEAR El Vallenatero Francés</span>'
    b = f'<span class="text-muted">&copy; {datetime.date.today().year} El Vallenatero Francés</span>'
    index_data = index_data.replace(a, b)
    page404_data = page404_data.replace(a, b)
    index_aprender_data = index_aprender_data.replace(a, b)

    # Save edited prod files
    with open(f"{output_prod_folder}/index.html", "w") as file:
        file.write(index_data)
    with open(f"{output_prod_folder}/404.html", "w") as file:
        file.write(page404_data)
    with open(f"{output_prod_folder}/aprender/index.html", "w") as file:
        file.write(index_aprender_data)

    # Create full HTML pages for Prod /aprender tutorials
    with open("../website/src/aprender/tutoriales.js") as in_file:
        # Remove the JS bits to keep only the JSON content
        tutoriales_json_content = in_file.read()[17:-2]
        tutoriales = json.loads(tutoriales_json_content)
        num_html_pages_created += len(tutoriales)
    for t in tutoriales:
        output_prod_tutorial_file = "{}/aprender/{}.html".format(
            output_prod_folder, t["slug"]
        )
        shutil.copy(
            f"{output_prod_folder}/aprender/index.html", output_prod_tutorial_file
        )
        with open(output_prod_tutorial_file, "r") as file:
            prod_tutorial_file_data = file.read()
        if t["author"]:
            tuto_title = "{} - {}".format(t["title"], t["author"])
        else:
            tuto_title = t["title"]
        prod_tutorial_file_data = prod_tutorial_file_data.replace(
            "<title>Aprender a tocar el Acordeón Vallenato - El Vallenatero Francés</title>",
            f"<title>{tuto_title} - Aprender a tocar el Acordeón Vallenato</title>",
        )
        prod_tutorial_file_data = prod_tutorial_file_data.replace(
            '<h1 id="tutorialFullTitle">TITLE</h1>',
            f'<h1 id="tutorialFullTitle">{tuto_title}</h1>',
        )
        with open(output_prod_tutorial_file, "w") as file:
            file.write(prod_tutorial_file_data)

    # Create full HTML pages for Prod / videos
    with open("../website/src/data.js") as in_file:
        # Remove the JS bits to keep only the JSON content
        videos_json_content = in_file.read()[16:-1]
        locations = json.loads(videos_json_content)
        num_html_pages_created += len(locations)
    for l in locations:
        # One page for each location
        output_prod_video_file = "{}/{}.html".format(
            output_prod_folder, locations[l]["slug"]
        )
        shutil.copy(f"{output_prod_folder}/index.html", output_prod_video_file)
        with open(output_prod_video_file, "r") as file:
            prod_video_file_data = file.read()
        tuto_title = l
        prod_video_file_data = prod_video_file_data.replace(
            "<title>El Vallenatero Francés</title>",
            f"<title>{tuto_title} - El Vallenatero Francés</title>",
        )
        prod_video_file_data = prod_video_file_data.replace(
            '<h2 id="list_location"></h2>', f'<h2 id="list_location">{tuto_title}</h2>'
        )
        with open(output_prod_video_file, "w") as file:
            file.write(prod_video_file_data)

        num_html_pages_created += len(locations[l]["videos"])
        for v in locations[l]["videos"]:
            # One page for each video at that location
            # Create folder
            output_folder = "{}/{}".format(output_prod_folder, v["slug"])
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)
            output_prod_video_file = "{}/{}.html".format(output_folder, v["id"])
            shutil.copy(f"{output_prod_folder}/index.html", output_prod_video_file)
            with open(output_prod_video_file, "r") as file:
                prod_video_file_data = file.read()
            tuto_title = v["title"]
            prod_video_file_data = prod_video_file_data.replace(
                "<title>El Vallenatero Francés</title>",
                f"<title>{tuto_title} - El Vallenatero Francés</title>",
            )
            prod_video_file_data = prod_video_file_data.replace(
                '<h2 id="list_location"></h2>',
                f'<h2 id="list_location">{tuto_title}</h2>',
            )
            with open(output_prod_video_file, "w") as file:
                file.write(prod_video_file_data)

    logger.debug(f"Number of production HTML files created: {num_html_pages_created}")


def generate_sitemap(sitemap_file, locations, uploaded_videos):
    logger.debug("Generate the Sitemap")
    base_url = "https://vallenato.fr"
    sitemap = generator.Sitemap()

    # vallenato.fr index
    sitemap.add(
        base_url,
        # Timestamp of the most recently uploaded video
        lastmod=uploaded_videos[0]["publishedAt"][:10],
        changefreq="monthly",
        priority="1.0",
    )

    # Locations and individual videos
    sitemap.add(
        f"{base_url}/mundo-entero",
        # Timestamp of the most recently uploaded video
        lastmod=uploaded_videos[0]["publishedAt"][:10],
        changefreq="monthly",
        priority="0.8",
    )
    for l in locations:
        # Locations
        sitemap.add(
            "{}/{}".format(base_url, locations[l]["slug"]),
            # Timestamp of the most recently uploaded video at that location
            lastmod=locations[l]["videos"][0]["publishedAt"][:10],
            changefreq="yearly",
            priority="0.6",
        )
        for v in locations[l]["videos"]:
            # Individual videos
            sitemap.add(
                "{}/{}/{}".format(base_url, v["slug"], v["id"]),
                # Timestamp of that video
                lastmod=v["publishedAt"][:10],
                changefreq="yearly",
                priority="0.5",
            )

    # Aprender index
    sitemap.add(f"{base_url}/aprender/", changefreq="monthly", priority="0.9")

    # Aprender: individual tutorials
    with open("../website/src/aprender/tutoriales.js") as in_file:
        # Remove the JS bits to keep only the JSON content
        tutoriales_json_content = in_file.read()[17:-2]
        tutoriales = json.loads(tutoriales_json_content)
    for t in tutoriales:
        tuto_url = "{}/aprender/{}".format(base_url, t["slug"])
        sitemap.add(tuto_url, changefreq="yearly", priority="0.7")

    sitemap_xml = sitemap.generate()

    # Prettify the XML "by hand"
    sitemap_xml = sitemap_xml.replace("<url>", "  <url>")
    sitemap_xml = sitemap_xml.replace("</url>", "  </url>")
    sitemap_xml = sitemap_xml.replace("<loc>", "    <loc>")
    sitemap_xml = sitemap_xml.replace("<lastmod>", "    <lastmod>")
    sitemap_xml = sitemap_xml.replace("<changefreq>", "    <changefreq>")
    sitemap_xml = sitemap_xml.replace("<priority>", "    <priority>")

    with open(sitemap_file, "w") as file:
        file.write(sitemap_xml)


def website(args):
    if getattr(args, "no_fetch", False):
        # Rebuild from the already-committed data instead of hitting the
        # YouTube API - locations/videos already have their slugs set, so
        # there's nothing left to do but regenerate the website files.
        locations = load_locations_from_website_data_file(WEBSITE_DATA_FILE)
        uploaded_videos = flatten_videos_from_locations(locations)
        logger.info(
            f"There are {len(uploaded_videos)} videos loaded from {WEBSITE_DATA_FILE} (--no-fetch)."
        )
    else:
        # Retrieve the list of uploaded videos
        uploaded_videos = get_uploaded_videos(args, UPLOADED_VIDEOS_DUMP_FILE)
        logger.info(f"There are {len(uploaded_videos)} uploaded videos.")

        # Identify each video's location
        (uploaded_videos, locations) = identify_locations_names(
            uploaded_videos, LOCATION_SPECIAL_CASES_FILE, UPLOADED_VIDEOS_DUMP_FILE
        )

        # Determine the geolocation of each location
        locations = determine_geolocation(locations, GEOLOCATIONS_FILE)

        # Create a slug for each location (to be used for the website URLs)
        locations = determine_locations_slug(locations)

        # Add the videos in each location array
        locations = add_videos_to_locations_array(uploaded_videos, locations)

        # Generate the JavaScript data file to be used by the website
        save_website_data(locations, WEBSITE_DATA_FILE)

    # Generate the development and production website files
    generate_website(locations, uploaded_videos)

    # Generate the Sitemap
    generate_sitemap(SITEMAP_FILE, locations, uploaded_videos)
