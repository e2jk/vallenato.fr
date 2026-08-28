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

import json
import logging
import os
import re
import readline
import shutil
import sys
import webbrowser
from urllib.error import HTTPError

from pytube import YouTube
from slugify import slugify

logger = logging.getLogger(__name__)

# File that contains the list of available tutorials
TUTORIALES_DATA_FILE = "../website/src/aprender/tutoriales.js"


def get_tutorial_info():
    """Retrieve the information of the new tutorial"""
    # What is the YouTube tutorial video?
    (tutorial_id, tutorial_url) = get_youtube_url("tutorial")
    # What is the YouTube full video?
    (full_video_id, full_video_url) = get_youtube_url("full")
    # Song title, author name and the tutorial creator's name and YouTube channel
    (song_title, song_author, tutocreator, tutocreator_channel, yt_tutorial_video) = (
        get_title_author_tutocreator_and_channel(tutorial_url)
    )
    # Tutorial's slug
    tutorial_slug = get_tutorial_slug(song_title)
    return (
        tutorial_id,
        tutorial_url,
        full_video_id,
        full_video_url,
        song_title,
        song_author,
        tutocreator,
        tutocreator_channel,
        yt_tutorial_video,
        tutorial_slug,
    )


def get_youtube_url(type):
    """Extract video ID and Normalize URL"""
    video_id = None
    video_url = None
    s = input(f"Enter the ID or URL of the {type} video ('q' to quit): ")
    while not video_id:
        if s.lower() == "q":
            print("Exiting...")
            sys.exit(10)
        video_id = youtube_url_validation(s)
        if not video_id:
            s = input(f"Invalid {type} video URL, please try again ('q' to quit): ")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return (video_id, video_url)


def youtube_url_validation(url):
    """Check that it is a valid YouTube URL.
    Inspired from https://stackoverflow.com/a/19161373
    """
    # Accept just the YouTube ID
    if re.match("^[a-zA-Z0-9_-]{11}$", url):
        return url
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([a-zA-Z0-9_-]{11})"
    )
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return youtube_regex_match


def get_title_author_tutocreator_and_channel(url):
    logger.debug(f"Downloading information from tutorial video '{url}'.")
    yt = YouTube(url)

    # Extract the title
    song_title = rlinput("Song title ('q' to quit): ", yt.title)
    if song_title.lower() == "q":
        print("Exiting...")
        sys.exit(11)

    # Extract the author's name
    song_author = rlinput("Song author ('q' to quit): ", yt.title)
    if song_author.lower() == "q":
        print("Exiting...")
        sys.exit(12)

    # The name of the creator of the tutorial
    tutocreator = yt.author

    # The YouTube channel of the creator of the tutorial
    # TODO: this broke when migrating to pytube3
    tutocreator_channel = "UPDATE MANUALLY"
    # tutocreator_channel = yt.player_config_args["player_response"]["videoDetails"]["channelId"]

    return (song_title, song_author, tutocreator, tutocreator_channel, yt)


def rlinput(prompt, prefill=""):
    """Provide an editable input string
    Inspired from https://stackoverflow.com/a/36607077
    """
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def get_existing_tutorial_slug():
    # Get the list of existing tutorial slugs
    with open(TUTORIALES_DATA_FILE) as in_file:
        # Remove the JS bits to keep only the JSON content
        tutoriales_json_content = in_file.read()[17:-2]
        tutoriales = json.loads(tutoriales_json_content)
    tutorials_slugs = [t["slug"] for t in tutoriales]
    return tutorials_slugs


def get_tutorial_slug(song_title):
    tutorials_slugs = get_existing_tutorial_slug()
    tutorial_slug = get_suggested_tutorial_slug(song_title, tutorials_slugs)
    # Propose the slug to the user
    tutorial_slug = rlinput("Tutorial slug/nice URL ('q' to quit): ", tutorial_slug)
    if tutorial_slug.lower() == "q":
        print("Exiting...")
        sys.exit(13)
    while tutorial_slug in tutorials_slugs:
        logger.debug(f"The slug '{tutorial_slug}' is already used.")
        tutorial_slug = rlinput("Tutorial slug/nice URL ('q' to quit): ", tutorial_slug)
        if tutorial_slug.lower() == "q":
            print("Exiting...")
            sys.exit(14)
    return tutorial_slug


def get_suggested_tutorial_slug(song_title, tutorials_slugs):
    # This tutorial's default slug
    tutorial_slug_base = slugify(song_title)
    tutorial_slug = tutorial_slug_base

    i = 1
    # Even if this slug is not used, check if maybe the -1 version is already used
    # This would be the case if there's already a -1 and -2 version
    if (
        tutorial_slug not in tutorials_slugs
        and f"{tutorial_slug_base}-{i}" in tutorials_slugs
    ):
        tutorial_slug = f"{tutorial_slug_base}-{i}"
    while tutorial_slug in tutorials_slugs:
        logger.debug(f"The slug '{tutorial_slug}' is already used.")
        i += 1
        tutorial_slug = f"{tutorial_slug_base}-{i}"
    return tutorial_slug


def determine_output_folder(temp_folder, tutorial_slug):
    output_folder = "../website/src/aprender/"
    if temp_folder:
        # Create a new temporary folder for this new tutorial
        output_folder += f"temp/{tutorial_slug}/"
        logger.debug(
            f"This new tutorial will be created in '{output_folder}' due to --temp-folder parameter."
        )
        if os.path.exists(output_folder):
            # Ask if the existing temporary folder should be deleted or the script ended
            logger.debug("The temporary folder already exists")
            s = input(
                "The temporary folder already exists, enter 'Y' to delete the folder or 'N' to stop the program: "
            )
            valid_entry = False
            while not valid_entry:
                if s.lower() == "y":
                    shutil.rmtree(output_folder)
                    valid_entry = True
                elif s.lower() == "n":
                    print("Exiting...")
                    sys.exit(15)
                else:
                    s = input(
                        "Enter 'Y' to delete the folder or 'N' to stop the program: "
                    )

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    return output_folder


def download_videos(
    yt_tutorial_video, tutorial_id, full_video_id, videos_output_folder
):
    # Tutorial video
    logger.info(f"Will now download the tutorial video {tutorial_id}...")
    download_youtube_video(yt_tutorial_video, tutorial_id, videos_output_folder)
    # Full video
    logger.info(f"Will now download the full video {full_video_id}...")
    # For the tutorial video we already had a Youtube object, not yet for the full video
    video_url = f"https://www.youtube.com/watch?v={full_video_id}"
    yt_full_video = YouTube(video_url)
    download_youtube_video(yt_full_video, full_video_id, videos_output_folder)


def download_youtube_video(yt, video_id, videos_output_folder):
    # Download stream with itag 18 by default:
    # <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">
    stream = yt.streams.get_by_itag(18)
    if not stream:
        logger.debug("No stream available with itag 18")
        stream = yt.streams.filter(
            res="360p", progressive=True, file_extension="mp4"
        ).first()
    logger.debug(f"Stream that will be downloaded: {stream}")
    logger.debug(f"Download folder: {videos_output_folder}")
    try:
        download_stream(stream, videos_output_folder, video_id)
    except HTTPError as e:
        logger.error(f"An HTTP error {e.code} occurred with reason: {e.reason}")
        # Propose to download that video manually from the browser
        webbrowser.open(f"https://y2mate.com/youtube/{video_id}", new=2, autoraise=True)
        return False
    return True


def download_stream(stream, videos_output_folder, video_id):
    stream.download(videos_output_folder, video_id)


def generate_new_tutorial_info(
    tutorial_slug, song_author, song_title, tutorial_id, full_video_id
):
    new_tutorial_info = f"""{{
    "slug": "{tutorial_slug}",
    "author": "{song_author}",
    "title": "{song_title}",
    "videos": [
      {{"id": "{tutorial_id}", "start": 0, "end": 999}}
    ],
    "videos_full_tutorial": [],
    "full_version": "{full_video_id}"
  }}"""
    return new_tutorial_info


def update_tutoriales_data_file(tutoriales_data_file, new_tutorial_info):
    # Read in the tutoriales data file
    with open(tutoriales_data_file, "r") as file:
        filedata = file.read()
    # Add the new tutorial info to the list of tutorials
    filedata = filedata.replace("}\n];", f"}},\n  {new_tutorial_info}\n];")
    # Save edited file
    with open(tutoriales_data_file, "w") as file:
        file.write(filedata)


def index_new_tutorial_link(tutorial_slug, song_title, song_author):
    return f"""\n              <div class="card mb-3" style="max-width: 17rem;">
                <div class="card-body">
                  <h5 class="card-title">{song_title} - {song_author}</h5>
                  <a href="{tutorial_slug}" class="stretched-link text-hide">Ver el tutorial</a>
                </div>
                <div class="card-footer"><small class="text-muted">NNmNNs en NN partes</small></div>
              </div>"""


def index_new_youtube_links(
    song_title, song_author, tutorial_url, tutocreator_channel, tutocreator
):
    return f'\n              <li>{song_title} - {song_author}: <a href="{tutorial_url}">Tutorial en YouTube</a> por <a href="https://www.youtube.com/channel/{tutocreator_channel}">{tutocreator}</a></li>'


def dummy_index_update(
    tutorial_slug,
    song_title,
    song_author,
    tutorial_url,
    tutocreator_channel,
    tutocreator,
    output_folder,
):
    dummy_index_page = f"{output_folder}index-dummy.html"
    logger.info(
        f"Creating a new dummy index page '{dummy_index_page}' with links to be included later in the main index page."
    )
    filedata = index_new_tutorial_link(tutorial_slug, song_title, song_author)
    filedata += index_new_youtube_links(
        song_title, song_author, tutorial_url, tutocreator_channel, tutocreator
    )
    with open(dummy_index_page, "w") as file:
        file.write(filedata)


def dummy_symlink_files(output_folder):
    logger.debug(
        f"Creating symlinks for the .js and .css files in the dummy folder '{output_folder}'."
    )
    os.symlink("../../vallenato.fr.js", f"{output_folder}vallenato.fr.js")
    os.symlink("../../vallenato.fr.css", f"{output_folder}vallenato.fr.css")


def update_index_page(
    tutorial_slug,
    song_title,
    song_author,
    tutorial_url,
    tutocreator_channel,
    tutocreator,
):
    logger.info("Updating the index page with links to the new tutorial page.")
    # Read in the index page
    with open("../website/src/aprender/index.html", "r") as file:
        filedata = file.read()

    # Add a link to the new tutorial's page
    end_section = """
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md">
            <h2>Otros recursos</h2>"""
    new_link = index_new_tutorial_link(tutorial_slug, song_title, song_author)
    tut_number = filedata.count("<!-- Tutorial ") + 1
    # TODO: add "wrap every N on ZZ" depending on the tutorial's number
    filedata = filedata.replace(
        end_section,
        f"\n              <!-- Tutorial {tut_number} -->{new_link}\n{end_section}",
    )

    # Add links to the tutorial and the author's YouTube channel
    end_section = "\n            </ul>\n          </div>\n        </div>\n      </div>\n    </main>\n    <!-- End page content -->"
    new_link = index_new_youtube_links(
        song_title, song_author, tutorial_url, tutocreator_channel, tutocreator
    )
    filedata = filedata.replace(end_section, f"{new_link}{end_section}")

    # Save edited file
    with open("../website/src/aprender/index.html", "w") as file:
        file.write(filedata)


def aprender(args):
    # Get the information about this new tutorial
    (
        tutorial_id,
        tutorial_url,
        full_video_id,
        _full_video_url,
        song_title,
        song_author,
        tutocreator,
        tutocreator_channel,
        yt_tutorial_video,
        tutorial_slug,
    ) = get_tutorial_info()

    # Determine the output folder (depends on the --temp-folder parameter)
    output_folder = determine_output_folder(args.temp_folder, tutorial_slug)

    # Get the info that will be added for the new tutorial
    new_tutorial_info = generate_new_tutorial_info(
        tutorial_slug, song_author, song_title, tutorial_id, full_video_id
    )

    if args.temp_folder:
        # When creating the new tutorial in a temporary folder for later edition,  do not update the index page
        dummy_index_update(
            tutorial_slug,
            song_title,
            song_author,
            tutorial_url,
            tutocreator_channel,
            tutocreator,
            output_folder,
        )
        # Symlink files so that the new template can be used from the temp folder
        dummy_symlink_files(output_folder)
    else:
        # Update the index page with the links to the new tutorial and to the tuto's author page
        update_index_page(
            tutorial_slug,
            song_title,
            song_author,
            tutorial_url,
            tutocreator_channel,
            tutocreator,
        )
        # Add the new tutorial to the list of tutorials
        update_tutoriales_data_file(TUTORIALES_DATA_FILE, new_tutorial_info)

    # Download the videos (both the tutorial and the full video)
    if args.no_download:
        logger.info(
            "Not downloading the videos from YouTube due to --no-download parameter."
        )
    else:
        videos_output_folder = f"{output_folder}videos/{tutorial_slug}/"
        if not os.path.exists(videos_output_folder):
            logger.debug(f"Creating folder '{videos_output_folder}'.")
            os.makedirs(videos_output_folder)
        download_videos(
            yt_tutorial_video, tutorial_id, full_video_id, videos_output_folder
        )

    # Open the new tutorial page in the webbrowser (new tab) for edition
    new_tutorial_page = f"http://localhost:8000/aprender/?new_tutorial={tutorial_slug}"
    logger.debug(f"Opening new tab in web browser to '{new_tutorial_page}'")
    webbrowser.open(new_tutorial_page, new=2, autoraise=True)
