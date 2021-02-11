"""
    sphinxnotes.khufu.snippet.filter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO: interactive filtering / selector

    Interactive filter for sphinxnotes.khufu.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import subprocess

from .cache import Cache

class Filter(ABC):
    @abstractmethod
    def filter(self, filename:str, keywords:List[str]=[]) -> None:
        pass


class FzfFilter(Filter):
    _cache:Cache

    def __init__(self, cache:Cache):
        self._cache = cache


    # TODO: preview backend
    def filter(self, keywords:List[str]=[]) -> str:
        preview_cmd = '"bat --style=plain --color=always %s"' %  self._cache.previewfile('{1}')
        fzf_args = ['fzf',
                    '--with-nth', '2..', # Hide first column (ID)
                    '--header-lines', '1', # Treat first line as header
                    '--preview', preview_cmd,
                    '--preview-window', 'up',
                    '--no-hscroll',
                    ]
        if keywords:
            fzf_args += ['--query', ' '.join(keywords)]
        output_args = ['cut', '-d', '" "', '-f', '1']
        args = fzf_args + ['|'] + output_args
        try:
            p = subprocess.Popen(['sh', '-c', ' '.join(args)],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

            from ..utils import ellipsis
            header = '%s  %s  %s  %s\n' % (
                'ID',
                ellipsis.ellipsis('Excerpt', 100, blank_sym=' '),
                ellipsis.ellipsis('Path', 50, blank_sym=' ' ),
                'Keywords')
            p.stdin.write(header.encode('utf-8'))
            for index in self._cache.indexes.values():
                row = '%s  %s  %s  %s\n' % (
                    index[0], # ID
                    ellipsis.ellipsis(index[1], 100, blank_sym=' '), # Excerpt
                    ellipsis.join(index[2], 50, 20, blank_sym=' ' ), # Titleppath
                    ','.join(index[3])) # Keywords
                p.stdin.write(row.encode('utf-8'))
                p.stdin.flush()
            p.stdin.close()
        except Exception as e:
            raise e
        p.wait()
        return p.stdout.read().decode('utf-8').strip().replace('\n', '')


    # TODO: preview backend
    def view(self, uid:str) -> None:
        args = ['bat', self._cache.previewfile(uid),
                '--color', 'always',
                '--style', 'plain',
                '--paging', 'always',
                ]
        try:
            _ = subprocess.run(args)
        except OSError as e:
            raise e
