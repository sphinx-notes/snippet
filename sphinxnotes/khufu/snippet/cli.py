"""
    sphinxnotes.khufu.snippet.cli
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Command line interface for sphinxnotes.khufu.snippet

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

import argparse
from os import path

from .filter import Filter, FzfFilter
from .cache import Cache
from .. import config


cachedir = config.load()['khufu']['cachedir']


def _load_cache() -> Cache:
    cache = Cache()
    cache.load(cachedir)
    return cache


def _on_command_show(args:argparse.Namespace):
    cache = _load_cache()

    if args.target:
        for uid in args.target:
            print(cache.get(uid))
    elif args.list_target:
        # TODO
        pass
    else:
        print('Snippet cache loaded from %s' % cachedir)
        print('I have %d targets' % len(cache.items()))


def _on_command_view(args:argparse.Namespace):
    """Entrypoint of snippet subcommand"""
    filter:Filter = FzfFilter()
    filter.filter(path.join(cachedir, 'index.txt'), keywords=args.keywords)


def init(subparsers:argparse.ArgumentParser) -> None:
    # Init snippet subcommand argument parser
    parser = subparsers.add_parser('snippet', aliases=['s', 'sni'],
        description='Tool for taking advantage of snippet in documentations.')
    subsubparsers = parser.add_subparsers()

    showparser = subsubparsers.add_parser('show', aliases=['sh'],
        description='Show infomation about snippets.')
    showparser.add_argument('target', nargs='*', help='Target ID to be shown')
    showparser.add_argument('--list-index', '-i', action='store_true',
                            help='List all indexes and the ID they points to')
    showparser.add_argument('--list-target', '-t', action='store_true',
                            help='List all target IDs')
    showparser.set_defaults(func=_on_command_show)
    
    viewparser = subsubparsers.add_parser('search', aliases=['s', 'se'],
        description='Search and view snippets.')
    viewparser.add_argument('keywords', nargs='*', default=[])
    viewparser.set_defaults(func=_on_command_view)
