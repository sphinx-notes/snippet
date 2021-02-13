"""
    sphinxnotes.khufu
    ~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import sys
import argparse
from typing import List

from .cli import snippet

__title__= 'sphinxnotes-khufu'
__license__ = 'BSD',
__version__ = '1.0a6'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/khufu'
__description__ = 'Non-intrusive utilities for Sphinx documentation'
__keywords__ = 'documentation, sphinx, extension, utility'

def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Add subparsers from sub modules
    subparsers = parser.add_subparsers()

    # Init submodules
    snippet.init(subparsers)

    # Parse command line arguments
    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
