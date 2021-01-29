"""
    sphinxnotes.khufu.cli.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Command line interface for sphinxnotes.khufu.snippet

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse

from .. import config
from ..snippet.filter import Filter, FzfFilter
from ..snippet.cache import Cache


def _load_cache() -> Cache:
    cache = Cache(config.load()['khufu']['cachedir'])
    cache.load()
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
        print('Snippet cache loaded from %s' % cache.dirname)
        print('I have %d snippet(s)' % len(cache.items()))


def _on_command_view(args:argparse.Namespace):
    cache = _load_cache()
    filter:Filter = FzfFilter(cache)
    uid = filter.filter(keywords=args.keywords)
    if uid:
        filter.view(uid)


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
