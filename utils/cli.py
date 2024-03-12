#!/usr/bin/python3
#
# Temporary command line entrypoint of snippet for test purpose.

import os
import sys
sys.path.insert(0, os.path.abspath('src/sphinxnotes'))
import snippet.cli

snippet.cli.main()
