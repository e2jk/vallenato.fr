#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://realpython.com/python-testing/

# Running the tests:
# $ python -m unittest -v test
# Checking the coverage of the tests:
# $ coverage run --include=vallenato_fr.py tests/test.py && coverage html

import unittest
import sys

sys.path.append('.')
target = __import__("vallenato_fr")

class TestInitMain(unittest.TestCase):
    def test_init_main_no_arguments(self):
        """
        Test the initialization code without any parameter
        """
        # Make the script believe we ran it directly
        target.__name__ = "__main__"
        # Pass it no arguments
        target.sys.argv = ["scriptname.py"]
        # Run the init(), nothing specific should happen, the program exits correctly
        target.init()

if __name__ == '__main__':
    unittest.main()
