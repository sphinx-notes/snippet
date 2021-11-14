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
from shutil import get_terminal_size
import posixpath

from xdg.BaseDirectory import xdg_config_home

from . import __title__, __version__, __description__
from .config import Config
from .cache import Cache
from .table import tablify, COLUMNS

DEFAULT_CONFIG_FILE = path.join(xdg_config_home, *__title__.split('-'), 'conf.py')

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawDescriptionHelpFormatter): pass


def get_integration_file(fn:str) -> str:
    """
    Get file path of integration files.

    .. note:: files are included by ``setup(package_data=xxx)``
    """
    prefix = path.abspath(path.dirname(__file__))
    return path.join(prefix, 'integration', fn)


def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__,
                                     formatter_class=HelpFormatter,
                                     epilog=dedent("""
                                     snippet tags:
                                       d (document)          a reST document 
                                       s (section)           a reST section
                                       c (code)              snippet with code blocks
                                       * (any)               wildcard for any snippet"""))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE, help='path to configuration file')

    # Init subcommands
    subparsers = parser.add_subparsers()
    statparser = subparsers.add_parser('stat', aliases=['s'],
                                       formatter_class=HelpFormatter,
                                       help='show snippets statistic information')
    statparser.set_defaults(func=_on_command_stat)

    listparser = subparsers.add_parser('list', aliases=['l'],
                                       formatter_class=HelpFormatter,
                                       help='list snippet indexes, columns of indexes: %s' % COLUMNS)
    listparser.add_argument('--tags', '-t', type=str, default='*',
                            help='list specified tags only')
    listparser.add_argument('--width', '-w', type=int,
                            default=get_terminal_size((120, 0)).columns,
                            help='width in characters of output')
    listparser.set_defaults(func=_on_command_list)

    getparser = subparsers.add_parser('get', aliases=['g'],
                                      formatter_class=HelpFormatter,
                                      help='get information of snippet by index ID')
    getparser.add_argument('--file', '-f', action='store_true',
                           help='get source file path of snippet')
    getparser.add_argument('--line-start', action='store_true',
                           help='get line number where snippet starts in source file')
    getparser.add_argument('--line-end', action='store_true',
                           help='get line number where snippet ends in source file')
    getparser.add_argument('--text', '-t', action='store_true',
                           help='get source reStructuredText of snippet')
    getparser.add_argument('--url', '-u', action='store_true',
                           help='get URL of HTML documentation of snippet')
    getparser.add_argument('index_id', type=str, nargs='+', help='index ID')
    getparser.set_defaults(func=_on_command_get)

    igparser = subparsers.add_parser('integration', aliases=['i'],
                                      formatter_class=HelpFormatter,
                                      help='integration related commands')
    igparser.add_argument('--sh', '-s', action='store_true', help='dump bash shell integration script')
    igparser.add_argument('--sh-binding', action='store_true', help='dump recommended bash key binding')
    igparser.add_argument('--zsh', '-z', action='store_true', help='dump zsh integration script')
    igparser.add_argument('--zsh-binding', action='store_true', help='dump recommended zsh key binding')
    igparser.add_argument('--vim', '-v', action='store_true', help='dump (neo)vim integration script')
    igparser.add_argument('--vim-binding', action='store_true', help='dump recommended vim key binding')
    igparser.add_argument('--nvim-binding', action='store_true', help='dump recommended neovim key binding')
    igparser.set_defaults(func=_on_command_integration, parser=igparser)

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Load config from file
    if args.config == DEFAULT_CONFIG_FILE and not path.isfile(DEFAULT_CONFIG_FILE):
        print('the default configuration file does not exist, ignore it', file=sys.stderr)
        cfg = Config({})
    else:
        cfg = Config.load(args.config)
    setattr(args, 'cfg', cfg)

    # Load snippet cache
    cache = Cache(cfg.cache_dir)
    cache.load()
    setattr(args, 'cache', cache)

    # Call subcommand
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


def _on_command_stat(args:argparse.Namespace):
    cache = args.cache

    num_projects = len(cache.num_snippets_by_project)
    num_docs = len(cache.num_snippets_by_docid)
    num_snippets = sum(cache.num_snippets_by_project.values())
    print(f'snippets are loaded from {cache.dirname}')
    print(f'configuration are loaded from {args.config}')
    print(f'integration files are located at {get_integration_file("")}')
    print('')
    print(f'I have {num_projects} project(s), {num_docs} documentation(s) and {num_snippets} snippet(s)')
    for i, v in cache.num_snippets_by_project.items():
        print(f'project {i}:')
        print(f"\t {v} snippets(s)")


def _on_command_list(args:argparse.Namespace):
    rows = tablify(args.cache.indexes, args.tags, args.width)
    for row in rows:
        print(row)


def _on_command_get(args:argparse.Namespace):
    for index_id in args.index_id:
        item = args.cache.get_by_index_id(index_id)
        if not item:
            print('no such index ID', file=sys.stderr)
            sys.exit(1)
        if args.text:
            print('\n'.join(item.snippet.rst))
        if args.file:
            print(item.snippet.file)
        if args.url:
            # HACK: get doc id in better way
            doc_id, _ = args.cache.index_id_to_doc_id.get(index_id)
            base_url = args.cfg.base_urls.get(doc_id[0])
            if not base_url:
                print(f'base URL for project {doc_id[0]} not configurated', file=sys.stderr)
                sys.exit(1)
            url = posixpath.join(base_url, doc_id[1] + '.html')
            if item.snippet.refid:
                url +=  '#' + item.snippet.refid
            print(url)
        if args.line_start:
            print(item.snippet.lineno[0])
        if args.line_end:
            print(item.snippet.lineno[1])


def _on_command_integration(args:argparse.Namespace):
    if args.sh:
        with open(get_integration_file('plugin.sh'), 'r') as f:
            print(f.read())
    if args.sh_binding:
        with open(get_integration_file('binding.sh'), 'r') as f:
            print(f.read())
    if args.zsh:
        # Zsh plugin depends on Bash shell plugin
        with open(get_integration_file('plugin.sh'), 'r') as f:
            print(f.read())
    if args.zsh_binding:
        # Zsh binding depends on Bash shell binding
        with open(get_integration_file('binding.sh'), 'r') as f:
            print(f.read())
        with open(get_integration_file('binding.zsh'), 'r') as f:
            print(f.read())
    if args.vim:
        with open(get_integration_file('plugin.vim'), 'r') as f:
            print(f.read())
    if args.vim_binding:
        with open(get_integration_file('binding.vim'), 'r') as f:
            print(f.read())
    if args.nvim_binding:
        # NeoVim binding depends on Vim binding
        with open(get_integration_file('binding.vim'), 'r') as f:
            print(f.read())
        with open(get_integration_file('binding.nvim'), 'r') as f:
            print(f.read())

if __name__ == '__main__':
    sys.exit(main())
