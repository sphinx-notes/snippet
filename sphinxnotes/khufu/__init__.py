"""
    sphinxnotes.khufu
    ~~~~~~~~~~~~~~~~~

    Command line toolset for Sphinx documentation.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

import sys
import argparse
from typing import List

from .cli import snippet

__version__ = '1.0a0'

def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog='khufu',
                                     description='Command line toolset for Sphinx documentation.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Add subparsers from sub modules
    subparsers = parser.add_subparsers()

    # Init submodules
    snippet.init(subparsers)

    # Parse command line arguments
    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
