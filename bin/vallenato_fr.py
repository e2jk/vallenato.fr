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

import sys
import re
import readline
from slugify import slugify
import os
import shutil
from pytube import YouTube
import argparse
import logging
import webbrowser

def get_tutorial_info():
    """Retrieve the information of the new tutorial"""
    # What is the YouTube tutorial video?
    (tutorial_id, tutorial_url) = get_youtube_url("tutorial")
    # What is the YouTube full video?
    (full_video_id, full_video_url) = get_youtube_url("full")
    # Song title, author name and the tutorial creator's name and YouTube channel
    (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = get_title_author_tutocreator_and_channel(tutorial_url)
    # Tutorial's slug
    tutorial_slug = get_tutorial_slug(song_title)
    return (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video, tutorial_slug)

def get_youtube_url(type):
    """Extract video ID and Normalize URL"""
    video_id = None
    video_url = None
    s = input("Enter the ID or URL of the %s video ('q' to quit): " % type)
    while not video_id:
        if s.lower() == "q":
            print("Exiting...")
            sys.exit(10)
        video_id = youtube_url_validation(s)
        if not video_id:
            s = input("Invalid %s video URL, please try again ('q' to quit): " % type)
    video_url = "https://www.youtube.com/watch?v=%s" % video_id
    return (video_id, video_url)

def youtube_url_validation(url):
    """Check that it is a valid YouTube URL.
    Inspired from https://stackoverflow.com/a/19161373
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([a-zA-Z0-9_-]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return youtube_regex_match

def get_title_author_tutocreator_and_channel(url):
    logging.debug("Downloading information from tutorial video '%s'." % url)
    yt = YouTube(url)

    page_title = yt.player_config_args["player_response"]["videoDetails"]["title"]

    # Extract the title
    song_title = rlinput("Song title ('q' to quit): ", page_title)
    if song_title.lower() == "q":
        print("Exiting...")
        sys.exit(11)

    # Extract the author's name
    song_author = rlinput("Song author ('q' to quit): ", page_title)
    if song_author.lower() == "q":
        print("Exiting...")
        sys.exit(12)

    # The name of the creator of the tutorial
    tutocreator = yt.player_config_args["player_response"]["videoDetails"]["author"]

    # The YouTube channel of the creator of the tutorial
    tutocreator_channel = yt.player_config_args["player_response"]["videoDetails"]["channelId"]

    return (song_title, song_author, tutocreator, tutocreator_channel, yt)

def rlinput(prompt, prefill=''):
    """Provide an editable input string
    Inspired from https://stackoverflow.com/a/36607077
    """
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

def get_tutorial_slug(song_title):
    (tutorials_path, tutorial_slug) = get_suggested_tutorial_slug(song_title)
    # Propose the slug to the user
    tutorial_slug = rlinput("Tutorial slug/nice URL ('q' to quit): ", tutorial_slug)
    if tutorial_slug.lower() == "q":
        print("Exiting...")
        sys.exit(13)
    slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
    while os.path.isfile(slug_path):
        logging.debug("The path '%s' already exists." % slug_path)
        tutorial_slug = rlinput("Tutorial slug/nice URL ('q' to quit): ", tutorial_slug)
        if tutorial_slug.lower() == "q":
            print("Exiting...")
            sys.exit(14)
        slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
    return tutorial_slug

def get_suggested_tutorial_slug(song_title):
    tutorial_slug_base = slugify(song_title)
    tutorial_slug = tutorial_slug_base
    # Get the path of the folder one level up (where all the tutorials are)
    tutorials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Create the path with this slug name
    slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
    # Check if there is already a file with the slug-1 (would otherwise not
    # detect if there was already more than one tutorial for this song)
    slug_path_dash_one = os.path.abspath(os.path.join(tutorials_path, "%s-1.html" % tutorial_slug))
    if os.path.isfile(slug_path_dash_one):
        logging.debug("The path '%s' doesn't exists, but '%s' does." % (slug_path, slug_path_dash_one))
        slug_path = slug_path_dash_one
    i = 2
    # Check if slug not already used, otherwise increment (starting at 2)
    while os.path.isfile(slug_path):
        logging.debug("The path '%s' already exists." % slug_path)
        tutorial_slug = "%s-%d" % (tutorial_slug_base, i)
        slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
        i += 1
    return (tutorials_path, tutorial_slug)

def download_videos(yt_tutorial_video, tutorial_id, full_video_id, videos_output_folder):
    # Tutorial video
    logging.info("Will now download the tutorial video %s..." % tutorial_id)
    download_youtube_video(yt_tutorial_video, tutorial_id, videos_output_folder)
    # Full video
    logging.info("Will now download the full video %s..." % full_video_id)
    # For the tutorial video we already had a Youtube object, not yet for the full video
    video_url = "https://www.youtube.com/watch?v=%s" % full_video_id
    yt_full_video = YouTube(video_url)
    download_youtube_video(yt_full_video, full_video_id, videos_output_folder)

def download_youtube_video(yt, video_id, videos_output_folder):
    # Download stream with itag 18 by default:
    # <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">
    stream = yt.streams.get_by_itag(18)
    if not stream:
        logging.debug("No stream available with itag 18")
        stream = yt.streams.filter(res = "360p", progressive=True, file_extension = "mp4").first()
    logging.debug("Stream that will be downloaded: %s" % stream)
    logging.debug("Download folder: %s" % videos_output_folder)
    stream.download(videos_output_folder, video_id)

def create_new_tutorial_page(tutorial_slug, song_title, song_author, tutorial_id, full_video_id, new_tutorial_page):
    logging.info("Creating the new tutorial page '%s'." % new_tutorial_page)
    # Copy the template to a new file
    shutil.copy("template.html", new_tutorial_page)
    # Read in the file
    with open(new_tutorial_page, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("[[TITLE]]", "%s - %s" % (song_title, song_author))
    filedata = filedata.replace("[[TUTORIAL VIDEO ID]]", tutorial_id)
    filedata = filedata.replace("[[FULL VIDEO ID]]", full_video_id)

    # Save edited file
    with open(new_tutorial_page, 'w') as file:
        file.write(filedata)

def index_new_tutorial_link(tutorial_slug, song_title, song_author):
    return '\n      <li><a href="%s.html">%s - %s</a> - NNmNNs en NN partes</li>' % (tutorial_slug, song_title, song_author)

def index_new_youtube_links(song_title, song_author, tutorial_url, tutocreator_channel, tutocreator):
    return '\n      <li>%s - %s: <a href="%s">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/%s">%s</a></li>' % (song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)

def dummy_index_update(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator, output_folder):
    dummy_index_page = "%sindex-dummy.html" % output_folder
    logging.info("Creating a new dummy index page '%s' with links to be included later in the main index page." % dummy_index_page)
    filedata = index_new_tutorial_link(tutorial_slug, song_title, song_author)
    filedata += index_new_youtube_links(song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)
    with open(dummy_index_page, 'w') as file :
        file.write(filedata)

def dummy_symlink_files(output_folder):
    logging.debug("Creating symlinks for the .js and .css files in the dummy folder '%s'." % output_folder)
    os.symlink("../../vallenato.fr.js", "%svallenato.fr.js" % output_folder)
    os.symlink("../../vallenato.fr.css", "%svallenato.fr.css" % output_folder)

def update_index_page(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator):
    logging.info("Updating the index page with links to the new tutorial page.")
    # Read in the index page
    with open("../index.html", 'r') as file :
        filedata = file.read()

    # Add a link to the new tutorial's page
    end_section = '\n    </ul>\n    <h2>Otros recursos</h2>'
    new_link = index_new_tutorial_link(tutorial_slug, song_title, song_author)
    filedata = filedata.replace(end_section, "%s%s" %(new_link, end_section))

    # Add links to the tutorial and the author's YouTube channel
    end_section = '\n    </ul>\n    <p><a href="https://vallenato.fr">El Vallenatero Francés</a>'
    new_link = index_new_youtube_links(song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)
    filedata = filedata.replace(end_section, "%s%s" %(new_link, end_section))

    # Save edited file
    with open("../index.html", 'w') as file:
        file.write(filedata)

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Create new Vallenato.fr tutorial pages.")
    parser.add_argument("-tf", "--temp-folder", action='store_true', required=False, help="Create the new tutorial in the ./temp folder, do not update the index page with the new links.")
    parser.add_argument("-nd", "--no-download", action='store_true', required=False, help="Do not download the videos from YouTube.")
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    args = parser.parse_args(arguments)

    # Configure logging level
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
        args.logging_level = logging.getLevelName(args.loglevel)

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args

def main():
    # Parse the provided command-line arguments
    args = parse_args(sys.argv[1:])

    # Get the information about this new tutorial
    (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video, tutorial_slug) = get_tutorial_info()

    # Determine the output folder (depends on the --temp-folder parameter)
    output_folder = "../"
    if args.temp_folder:
        # Create a new temporary folder for this new tutorial
        output_folder += "temp/%s/" % tutorial_slug
        logging.debug("This new tutorial will be created in '%s' due to --temp-folder parameter." % output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # The file name for the new tutorial
    new_tutorial_page = "%s%s.html" % (output_folder, tutorial_slug)

    # Create the new tutorial's page
    create_new_tutorial_page(tutorial_slug, song_title, song_author, tutorial_id, full_video_id, new_tutorial_page)

    if args.temp_folder:
        # When creating the new tutorial in a temporary folder for later edition,  do not update the index page
        dummy_index_update(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator, output_folder)
        # Symlink files so that the new template can be used from the temp folder
        dummy_symlink_files(output_folder)
    else:
        # Update the index page with the links to the new tutorial and to the tuto's author page
        update_index_page(tutorial_slug, song_title, song_author, tutorial_url, tutocreator_channel, tutocreator)

    # Download the videos (both the tutorial and the full video)
    if args.no_download:
        logging.info("Not downloading the videos from YouTube due to --no-download parameter.")
    else:
        videos_output_folder = "%svideos/%s/" % (output_folder, tutorial_slug)
        if not os.path.exists(videos_output_folder):
            logging.debug("Creating folder '%s'." % videos_output_folder)
            os.makedirs(videos_output_folder)
        download_videos(yt_tutorial_video, tutorial_id, full_video_id, videos_output_folder)

    # Open the new tutorial page in the webbrowser (new tab) for edition
    logging.debug("Opening new tab in web browser to '%s'" % new_tutorial_page)
    webbrowser.open(new_tutorial_page, new=2, autoraise=True)

def init():
    if __name__ == "__main__":
        main()

init()
