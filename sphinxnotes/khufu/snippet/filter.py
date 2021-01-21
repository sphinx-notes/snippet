"""
    sphinxnotes.khufu.snippet.filter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO: interactive filtering / selector

    Interactive filter for sphinxnotes.khufu.snippet.
    
    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from abc import ABC, abstractmethod
from typing import List
import subprocess


class Filter(ABC):
    @abstractmethod
    def filter(self, filename:str, keywords:List[str]=[]) -> None:
        pass


class FzfFilter(Filter):
    # TODO: preview backend
    def filter(self, filename:str, keywords:List[str]=[]) -> None:
        input_args = ['cat', filename]
        fzf_args = ['fzf',
                '--with-nth', '2..', # Hide first column (ID)
                '--header-lines', '1', # Treat first line as header
                '--preview', '"bat --color=always {1}.rst"',
                '--preview-window', 'up',
                    ]
        if keywords:
            fzf_args += ['--query', ' '.join(keywords)]
        output_args = ['cut', '-d', '" "', '-f', '1']
        args = input_args + ['|'] + fzf_args + ['|'] + output_args
        try:
            p = subprocess.run(['sh', '-c', ' '.join(args)])
        except OSError as e:
            raise e
        print('Filtered:', p.stdout)
