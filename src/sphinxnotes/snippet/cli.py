"""
sphinxnotes.snippet.cli
~~~~~~~~~~~~~~~~~~~~~~~

Command line entrypoint.

:copyright: Copyright 2024 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

# **NOTE**: Import new packages with caution:
# Importing complex packages (like sphinx.*) will directly slow down the
# startup of the CLI tool.
from __future__ import annotations
import sys
import os
from os import path
import argparse
from typing import Iterable
from textwrap import dedent
from shutil import get_terminal_size
import posixpath

from xdg.BaseDirectory import xdg_config_home

from .snippets import Document
from .config import Config
from .cache import Cache, IndexID, Index
from .table import tablify, COLUMNS

DEFAULT_CONFIG_FILE = path.join(xdg_config_home, 'sphinxnotes', 'snippet', 'conf.py')


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def get_integration_file(fn: str) -> str:
    """
    Get file path of integration files.

    .. seealso::

       see ``[tool.setuptools.package-data]`` section of pyproject.toml to know
       how files are included.
    """
    # TODO: use https://docs.python.org/3/library/importlib.resources.html#importlib.resources.files
    prefix = path.abspath(path.dirname(__file__))
    return path.join(prefix, 'integration', fn)


def main(argv: list[str] = sys.argv[1:]):
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(
        prog=__name__,
        description='Sphinx documentation snippets manager',
        formatter_class=HelpFormatter,
        epilog=dedent("""
                                     snippet tags:
                                       d (document)          a reST document 
                                       s (section)           a reST section
                                       c (code)              snippet with code blocks
                                       * (any)               wildcard for any snippet"""),
    )
    parser.add_argument(
        '--version',
        # add_argument provides action='version', but it requires a version
        # literal and doesn't support lazily obtaining version.
        action='store_true',
        help="show program's version number and exit",
    )
    parser.add_argument(
        '-c', '--config', default=DEFAULT_CONFIG_FILE, help='path to configuration file'
    )

    # Init subcommands
    subparsers = parser.add_subparsers()
    statparser = subparsers.add_parser(
        'stat',
        aliases=['s'],
        formatter_class=HelpFormatter,
        help='show snippets statistic information',
    )
    statparser.set_defaults(func=_on_command_stat)

    listparser = subparsers.add_parser(
        'list',
        aliases=['l'],
        formatter_class=HelpFormatter,
        help='list snippet indexes, columns of indexes: %s' % COLUMNS,
    )
    listparser.add_argument(
        '--tags', '-t', type=str, default='*', help='list snippets with specified tags'
    )
    listparser.add_argument(
        '--docname',
        '-d',
        type=str,
        default='**',
        help='list snippets whose docname matches shell-style glob pattern',
    )
    listparser.add_argument(
        '--width',
        '-w',
        type=int,
        default=get_terminal_size((120, 0)).columns,
        help='width in characters of output',
    )
    listparser.set_defaults(func=_on_command_list)

    getparser = subparsers.add_parser(
        'get',
        aliases=['g'],
        formatter_class=HelpFormatter,
        help='get information of snippet by index ID',
    )
    getparser.add_argument(
        '--docname', '-d', action='store_true', help='get docname of snippet'
    )
    getparser.add_argument(
        '--file', '-f', action='store_true', help='get source file path of snippet'
    )
    getparser.add_argument(
        '--deps', action='store_true', help='get dependent files of document'
    )
    getparser.add_argument(
        '--line-start',
        action='store_true',
        help='get line number where snippet starts in source file',
    )
    getparser.add_argument(
        '--line-end',
        action='store_true',
        help='get line number where snippet ends in source file',
    )
    getparser.add_argument(
        '--text',
        '-t',
        action='store_true',
        help='get source reStructuredText of snippet',
    )
    getparser.add_argument(
        '--url',
        '-u',
        action='store_true',
        help='get URL of HTML documentation of snippet',
    )
    getparser.add_argument('index_id', type=str, nargs='+', help='index ID')
    getparser.set_defaults(func=_on_command_get)

    igparser = subparsers.add_parser(
        'integration',
        aliases=['i'],
        formatter_class=HelpFormatter,
        help='integration related commands',
    )
    igparser.add_argument(
        '--sh', '-s', action='store_true', help='dump bash shell integration script'
    )
    igparser.add_argument(
        '--sh-binding', action='store_true', help='dump recommended bash key binding'
    )
    igparser.add_argument(
        '--zsh', '-z', action='store_true', help='dump zsh integration script'
    )
    igparser.add_argument(
        '--zsh-binding', action='store_true', help='dump recommended zsh key binding'
    )
    igparser.add_argument(
        '--vim', '-v', action='store_true', help='dump (neo)vim integration script'
    )
    igparser.add_argument(
        '--vim-binding', action='store_true', help='dump recommended vim key binding'
    )
    igparser.add_argument(
        '--nvim-binding',
        action='store_true',
        help='dump recommended neovim key binding',
    )
    igparser.set_defaults(func=_on_command_integration, parser=igparser)

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Print version message.
    # See parser.add_argument('--version', ...) for more detais.
    if args.version:
        # NOTE: Importing is slow, do it on demand.
        from importlib.metadata import version

        pkgname = 'sphinxnotes.snippet'
        print(pkgname, version(pkgname))
        parser.exit()

    # Load config from file
    if args.config == DEFAULT_CONFIG_FILE and not path.isfile(DEFAULT_CONFIG_FILE):
        print(
            'the default configuration file does not exist, ignore it', file=sys.stderr
        )
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


def _on_command_stat(args: argparse.Namespace):
    cache = args.cache

    num_projects = len(cache.num_snippets_by_project)
    num_docs = len(cache.num_snippets_by_docid)
    num_snippets = sum(cache.num_snippets_by_project.values())
    print(f'snippets are loaded from {cache.dirname}')
    print(f'configuration are loaded from {args.config}')
    print(f'integration files are located at {get_integration_file("")}')
    print('')
    print(
        f'I have {num_projects} project(s), {num_docs} documentation(s) and {num_snippets} snippet(s)'
    )
    for i, v in cache.num_snippets_by_project.items():
        print(f'project {i}:')
        print(f'\t {v} snippets(s)')


def _filter_list_items(
    cache: Cache, tags: str, docname_glob: str
) -> Iterable[tuple[IndexID, Index]]:
    # NOTE: Importing is slow, do it on demand.
    from sphinx.util.matching import patmatch

    for index_id, index in cache.indexes.items():
        # Filter by tags.
        if index[0] not in tags and '*' not in tags:
            continue
        # Filter by docname.
        (_, docname), _ = cache.index_id_to_doc_id[index_id]
        if not patmatch(docname, docname_glob):
            continue
        yield (index_id, index)


def _on_command_list(args: argparse.Namespace):
    items = _filter_list_items(args.cache, args.tags, args.docname)
    for row in tablify(items, args.width):
        print(row)


def _on_command_get(args: argparse.Namespace):
    # Wrapper for warning when nothing is printed
    printed = False

    def p(*args, **opts):
        nonlocal printed
        printed = True
        print(*args, **opts)

    for index_id in args.index_id:
        item = args.cache.get_by_index_id(index_id)
        if not item:
            p('no such index ID', file=sys.stderr)
            sys.exit(1)
        if args.text:
            p('\n'.join(item.snippet.rst))
        if args.docname:
            p(item.snippet.docname)
        if args.file:
            p(item.snippet.file)
        if args.deps:
            if not isinstance(item.snippet, Document):
                print(
                    f'{type(item.snippet)} ({index_id}) is not a document',
                    file=sys.stderr,
                )
                sys.exit(1)
            if len(item.snippet.deps) == 0:
                p('')  # prevent print nothing warning
            for dep in item.snippet.deps:
                p(dep)
        if args.url:
            # HACK: get doc id in better way
            doc_id, _ = args.cache.index_id_to_doc_id.get(index_id)
            base_url = args.cfg.base_urls.get(doc_id[0])
            if not base_url:
                print(
                    f'base URL for project {doc_id[0]} not configurated',
                    file=sys.stderr,
                )
                sys.exit(1)
            url = posixpath.join(base_url, doc_id[1] + '.html')
            if item.snippet.refid:
                url += '#' + item.snippet.refid
            p(url)
        if args.line_start:
            p(item.snippet.lineno[0])
        if args.line_end:
            p(item.snippet.lineno[1])

        if not printed:
            print('please specify at least one argument', file=sys.stderr)
            sys.exit(1)


def _on_command_integration(args: argparse.Namespace):
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
    # Prevent "[Errno 32] Broken pipe" error.
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown.
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
