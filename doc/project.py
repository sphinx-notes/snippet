# -*- coding: utf-8 -*-
'''
Project Meta Information
~~~~~~~~~~~~~~~~~~~~~~~~
'''

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from sphinxnotes import khufu

name = 'sphinxnotes-khufu'
version = khufu.__version__
github_user = 'sphinx-notes'
github_repo = 'khufu'
url = 'https://github.com/' + github_user + '/' + github_repo
download_url = 'http://pypi.python.org/pypi/' + name
project_urls = {
    'Documentation': 'https://' + github_repo + '.github.io/' + github_repo,
    'Source': url,
    'Tracker': url + '/issues',
}
license = 'BSD',
author = 'Shengyu Zhang'
description = 'Command line toolset for Sphinx documentation'
keywords = 'documentation, sphinx, extension'
