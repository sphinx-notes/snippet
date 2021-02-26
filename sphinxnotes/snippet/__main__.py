"""
    sphinxnotes.snippet.__main__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import sys
import argparse
from typing import List

from . import __version__, __description__
from . import config
from .filter import Filter, FzfFilter
from .cache import Cache

def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # Init subcommands
    subparsers = parser.add_subparsers()
    showparser = subparsers.add_parser('show', aliases=['s'],
        description='Show infomation about snippets.')
    showparser.add_argument('snippet_ids', nargs='*', help='Snippet IDs to be shown')
    showparser.add_argument('--all', '-i', action='store_true',
                            help='List all snippets')
    showparser.set_defaults(func=_on_command_show)

    viewparser = subparsers.add_parser('view', aliases=['v'],
        description='View snippets from interactive filter.')
    viewparser.add_argument('keywords', nargs='*', default=[])
    viewparser.set_defaults(func=_on_command_view)

    editparser = subparsers.add_parser('edit', aliases=['e'],
        description='Execute code snippet from interactive filter.')
    editparser.add_argument('keywords', nargs='*', default=[])
    editparser.set_defaults(func=_on_command_edit)

    invokeparser = subparsers.add_parser('invoke', aliases=['i'],
        description='Clip snippet from interactive filter.')
    invokeparser.add_argument('keywords', nargs='*', default=[])
    invokeparser.set_defaults(func=_on_command_invoke)

    clipparser = subparsers.add_parser('clip', aliases=['c'],
        description='Clip snippet from interactive filter.')
    clipparser.add_argument('keywords', nargs='*', default=[])
    clipparser.set_defaults(func=_on_command_clip)

    # Parse command line arguments
    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)


def _load_cache() -> Cache:
    cache = Cache(config.load()['khufu']['cachedir'])
    cache.load()
    return cache


def _on_command_show(args:argparse.Namespace):
    cache = _load_cache()

    if args.snippet_ids:
        for uid in args.snippet_ids:
            print(cache.get(uid))
    elif args.all:
        for uid in cache.keys():
            print(uid)
    else:
        projects = []
        num_snippets = []
        num_docs = []
        for project in cache.tree:
            projects.append(project)
            num_docs.append(len(cache.tree[project]))
            num_snippets.append(sum([len(x) for x in cache.tree[project]]))
        print('Snippets are loaded from %s' % cache.dirname)
        print(f'I have {len(projects)} project(s), {sum(num_docs)} documentation(s) and {sum(num_snippets)} snippet(s)')
        for i, _ in enumerate(projects):
            print(f'Project {projects[i]}:')
            print(f"\t {num_docs[i]} documentation(s), {num_snippets[i]} snippets(s)")


def _on_command_view(args:argparse.Namespace):
    cache = _load_cache()
    filter:Filter = FzfFilter(cache)
    uid = filter.filter(keywords=args.keywords)
    if uid:
        filter.view(uid)


def _on_command_edit(args:argparse.Namespace):
    pass


def _on_command_invoke(args:argparse.Namespace):
    pass


def _on_command_clip(args:argparse.Namespace):
    pass

if __name__ == '__main__':
    sys.exit(main())
