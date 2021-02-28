"""
    sphinxnotes.snippet.cli
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import sys
import argparse
from typing import List
from os import path
from textwrap import dedent

from xdg.BaseDirectory import xdg_config_home

from . import __title__, __version__, __description__
from .config import Config
from .filter import Filter
from .cache import Cache

DEFAULT_CONFIG_FILE = path.join(xdg_config_home, __title__, 'conf.py')

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                  argparse.RawDescriptionHelpFormatter):
    pass

def add_subcommand_common_arguments(parser:argparse.ArgumentParser) -> None:
    """Add common arguments (partial) subcommands to subcommands' argument parser."""
    parser.add_argument('keywords', nargs='*', help='keywords for pre-filtering')
    parser.add_argument('--id', nargs=1, help='specify snippet by ID instead of filtering')
    parser.add_argument('--kind', '-k', nargs=1, help='snippet kind for pre-filtering')


def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__,
                                     # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     formatter_class=HelpFormatter,
                                     epilog=dedent("""
                                     snippet kinds:
                                       headline (d)          documentation title and possible subtitle
                                       code (c)              notes with code block
                                       procedure (p)         notes with a sequence of code for doing something (TODO)
                                       image (i)             notes with an image (TODO)"""))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE, help='path to configuration file')

    # Init subcommands
    subparsers = parser.add_subparsers()
    showparser = subparsers.add_parser('show', aliases=['s'],
        help='show snippets infomation')
    showparser.add_argument('ids', nargs='*', help='show infomation of specify snippet')
    showparser.add_argument('--list', '-l', action='store_true', help='list all snippets')
    showparser.set_defaults(func=_on_command_show)

    viewparser = subparsers.add_parser('view', aliases=['v'], help='filter and view snippet')
    viewparser.set_defaults(func=_on_command_view)

    editparser = subparsers.add_parser('edit', aliases=['e'], help='filter and edit snippet')
    editparser.set_defaults(func=_on_command_edit)

    invokeparser = subparsers.add_parser('invoke', aliases=['i'], help='filter and invoke executable snippet')
    invokeparser.set_defaults(func=_on_command_invoke)

    clipparser = subparsers.add_parser('clip', aliases=['c'], help='filter and clip snippet to clipboard')
    clipparser.set_defaults(func=_on_command_clip)

    # Add common arguments
    for p in [viewparser, editparser, invokeparser, clipparser]:
        add_subcommand_common_arguments(p)

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Load config from file
    if args.config == DEFAULT_CONFIG_FILE and not path.isfile(DEFAULT_CONFIG_FILE):
        print('the default configuration file does not exist, ignore it')
        cfg = Config({})
    else:
        cfg = Config.load(args.config)
    setattr(args, 'config', cfg)

    # Load snippet cache
    cache = Cache(cfg.cache_dir)
    cache.load()
    setattr(args, 'cache', cache)

    # Call subcommand
    if hasattr(args, 'func'):
        args.func(args)


def _on_command_show(args:argparse.Namespace):
    cache = args.cache
    if args.ids:
        for uid in args.ids:
            print(cache.get(uid))
    elif args.list:
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
        print('snippets are loaded from %s' % cache.dirname)
        print(f'I have {len(projects)} project(s), {sum(num_docs)} documentation(s) and {sum(num_snippets)} snippet(s)')
        for i, _ in enumerate(projects):
            print(f'project {projects[i]}:')
            print(f"\t {num_docs[i]} documentation(s), {num_snippets[i]} snippets(s)")


def _on_command_view(args:argparse.Namespace):
    filter = Filter(args.cache, args.config)
    uid = filter.filter(keywords=args.keywords)
    if uid:
        filter.view(uid)


def _on_command_edit(args:argparse.Namespace):
    filter = Filter(args.cache, args.config)
    uid = filter.filter(keywords=args.keywords)
    if uid:
        filter.edit(uid)


def _on_command_invoke(args:argparse.Namespace):
    pass


def _on_command_clip(args:argparse.Namespace):
    pass


if __name__ == '__main__':
    sys.exit(main())
