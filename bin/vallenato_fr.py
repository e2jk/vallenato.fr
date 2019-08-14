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

import argparse
import logging
import sys
from aprender import aprender
from website import website

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Update the Vallenato.fr website")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--aprender", action='store_true', required=False, help="Create a new tutorial for vallenato.fr/aprender")
    group.add_argument("-w", "--website", action='store_true', required=False, help="Regenerate the Vallenato.fr website (but not the /aprender section)")

    # These arguments are only to be used in conjunction with --aprender
    parser.add_argument("-tf", "--temp-folder", action='store_true', required=False, help="Create the new tutorial in the ./temp folder, do not update the index page with the new links")
    parser.add_argument("-nd", "--no-download", action='store_true', required=False, help="Do not download the videos from YouTube")

    # These arguments are only to be used in conjunction with --website
    #TODO
    parser.add_argument("-duv", "--dump-uploaded-videos", action='store_true', required=False, help="Dump the list of uploaded videos from YouTube, so as not to have to download it again")

    # General arguments (can be used both with --aprender and --website)
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

    # Validate if the arguments are used correctly
    if args.temp_folder and not args.aprender:
        logging.critical("The --temp-folder argument can only be used in conjunction with --aprender. Exiting...")
        sys.exit(16)
    if args.no_download and not args.aprender:
        logging.critical("The --no-download argument can only be used in conjunction with --aprender. Exiting...")
        sys.exit(17)
    if args.dump_uploaded_videos and not args.website:
        logging.critical("The --dump-uploaded-videos argument can only be used in conjunction with --website. Exiting...")
        sys.exit(18)

    # Configure logging level
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
        args.logging_level = logging.getLevelName(args.loglevel)

    # Needed for the Youtube integration
    args.noauth_local_webserver = True

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args

def main():
    # Parse the provided command-line arguments
    args = parse_args(sys.argv[1:])

    # --aprender
    if args.aprender:
        aprender(args)
    elif args.website:
        website(args)

def init():
    if __name__ == "__main__":
        main()

init()
