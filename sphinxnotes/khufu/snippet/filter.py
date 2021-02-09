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
        input_args = ['cat', self._cache.indexfile()]
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
        args = input_args + ['|'] + fzf_args + ['|'] + output_args
        try:
            p = subprocess.run(['sh', '-c', ' '.join(args)], stdout=subprocess.PIPE)
        except OSError as e:
            raise e
        if not p.stdout:
            raise p.stderr
        return p.stdout.decode('utf-8').strip().replace('\n', '')


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
