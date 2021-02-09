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


def init(subparsers:argparse.ArgumentParser) -> None:
    # Init snippet subcommand argument parser
    parser = subparsers.add_parser('snippet', aliases=['s', 'sni'],
        description='View and use snippets in sphinx documentations.')
    subsubparsers = parser.add_subparsers()

    showparser = subsubparsers.add_parser('show', aliases=['s'],
        description='Show infomation about snippets.')
    showparser.add_argument('snippet_ids', nargs='*', help='Snippet IDs to be shown')
    showparser.add_argument('--all', '-i', action='store_true',
                            help='List all snippets')
    showparser.set_defaults(func=_on_command_show)

    viewparser = subsubparsers.add_parser('view', aliases=['v'],
        description='View snippets from interactive filter.')
    viewparser.add_argument('keywords', nargs='*', default=[])
    viewparser.set_defaults(func=_on_command_view)

    execparser = subsubparsers.add_parser('exec', aliases=['e'],
        description='Execute code snippet from interactive filter.')
    execparser.add_argument('keywords', nargs='*', default=[])
    # execparser.set_defaults(func=_on_command_exec)

    clipparser = subsubparsers.add_parser('clip', aliases=['c'],
        description='Clip snippet from interactive filter.')
    clipparser.add_argument('keywords', nargs='*', default=[])
    # clipparser.set_defaults(func=_on_command_clip)
