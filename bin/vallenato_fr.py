#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

def get_tutorial_info():
    """Retrieve the information of the new tutorial"""
    # What is the YouTube tutorial video?
    (tutorial_id, tutorial_url) = get_youtube_url("tutorial")
    # What is the YouTube full video?
    (full_video_id, full_video_url) = get_youtube_url("full")
    # Song name
        # Autodetect, correct if needed
    # Author name
        # Autodetect, correct if needed
    # Tutorial's slug
        # Autodetect, correct if needed
        # Check if slug not already used

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
    get_tutorial_info()

def init():
    if __name__ == "__main__":
        main()

init()
