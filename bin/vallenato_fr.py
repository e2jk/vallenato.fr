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

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Create new Vallenato.fr tutorial pages.")
    parser.add_argument("-a", "--aprender", action='store_true', required=True, help="Create a new tutorial.")
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

    # --aprender
    if args.aprender:
        aprender(args)

def init():
    if __name__ == "__main__":
        main()

init()
