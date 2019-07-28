#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
from urllib.request import urlopen
import readline
from slugify import slugify
import os

def get_tutorial_info():
    """Retrieve the information of the new tutorial"""
    # What is the YouTube tutorial video?
    (tutorial_id, tutorial_url) = get_youtube_url("tutorial")
    # What is the YouTube full video?
    (full_video_id, full_video_url) = get_youtube_url("full")
    # Song title  and author name
    (song_title, song_author) = get_title_and_author(tutorial_url)
    # Tutorial's slug
    tutorial_slug = get_tutorial_slug(song_title)
    return (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutorial_slug)

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
    # print(video_id, video_url)
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

def get_title_and_author(url):
    # Download that page
    f = urlopen(url)
    # Read only the first 1000 characters, should contain the <title> tag
    myfile = f.read(10000).decode("utf-8")
    page_title = re.search("<title>(.*) - YouTube</title>", myfile).groups()[0]
    # page_title = "Muere una Flor - Turorial de Acordeón | Binomio de Oro"
    # print(page_title)

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

    return (song_title, song_author)

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
        tutorial_slug = rlinput("Tutorial slug/nice URL ('q' to quit): ", tutorial_slug)
        if tutorial_slug.lower() == "q":
            print("Exiting...")
            sys.exit(14)
        slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
    return slug_path


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
        slug_path = slug_path_dash_one
    i = 2
    while os.path.isfile(slug_path):
        # Check if slug not already used, otherwise increment (starting at 2)
        tutorial_slug = "%s-%d" % (tutorial_slug_base, i)
        slug_path = os.path.abspath(os.path.join(tutorials_path, "%s.html" % tutorial_slug))
        i += 1
    return (tutorials_path, tutorial_slug)

# Download the videos
    # Tutorial video
    # Full video

# Download a single video from YouTube

# Get the tutorial's author name and YouTube channel

# Create the new tutorial's page
    # Copy the template to a new file
    # Replace [[TITLE]]
    # Replace [[TUTORIAL VIDEO URL]]
    # Replace [[FULL VIDEO URL]]

# Update the index page
    # Link to the new tutorial's page
    # Link to the author's YouTube channel

def main():
    (tutorial_id, tutorial_url, full_video_id, full_video_url, song_title, song_author, tutorial_slug) = get_tutorial_info()

def init():
    if __name__ == "__main__":
        main()

init()
