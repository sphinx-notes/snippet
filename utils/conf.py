# Snippet confiuration for test purpose.

import os
import sys
sys.path.insert(0, os.path.abspath('sphinxnotes'))
from snippet.config import preset

cache_dir = '/tmp/sphinxnotes-snippet'
viewer = preset.rst2ansi_viewer
