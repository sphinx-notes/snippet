"""
    sphinxnotes.khufu
    ~~~~~~~~~~~~~~~~~

    Command line toolset for Sphinx documentation.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

import sys
import argparse

from .snippet.cli import init as snippet_init

def main():
    parser = argparse.ArgumentParser(prog='khufu',
                                     description='Command line toolset for Sphinx documentation.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0a0')
    # Add subparsers from sub modules
    subparsers = parser.add_subparsers()

    # Init submodules
    snippet_init(subparsers)

    # Parse command line argument
    args = parser.parse_args(sys.argv[1:])
    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
