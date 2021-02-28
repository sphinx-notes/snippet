"""
    sphinxnotes.snippet.config.preset
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Optional, List

def fzf_filter(columns:List[str],
               header_line:Optional[int]=None,
               keywords:List[str]=[]) -> List[str]:
    colid = columns.index('id') + 1
    args = ['fzf',
            '--with-nth', f'{colid+1}..', # Hide ID column FIXME
            '--no-hscroll',
            ]
    if False: # FIXME: impl preview
        args += ['--preview', 'xxx']
        args += ['--preview-window', 'up']
    if header_line:
        args += ['--header-lines', str(header_line)]
    if keywords:
        args += ['--query', ' '.join(keywords)]
    return args


def cat_viewer(filename:str, line:Optional[int]=None):
    return ['cat', filename]


def bat_viewer(filename:str, line:Optional[int]=None):
    args = ['bat', filename,
            '--color', 'always',
            '--style', 'plain',
            '--paging', 'always',
            ]
    if line:
        args += ['--highlight-line', str(line)]
    return args


def rst2ansi_viewer(filename:str, line:Optional[int]=None):
    return ['rst2ansi', filename]


def vim_editor(filename:str, line:Optional[int]=None) -> List[str]:
    args = ['vim']
    if line:
        args.append('+%s' % line)
    args.append(filename)
    return args
