"""
    sphinxnotes.khufu.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Search, view and apply snippet of Sphinx documentation.

    The module is also a Sphinx extension. please refer to documentation.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from .ext import setup
from .cli import init

init = init
setup = setup
