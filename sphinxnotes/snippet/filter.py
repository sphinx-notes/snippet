"""
    sphinxnotes.snippet.filter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO: interactive filtering / selector

    Interactive filter for sphinxnotes.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Optional
import sys
import subprocess
import shutil

from .cache import Cache
from .config import Config

COLUMNS = ['id', 'excerpt', 'path', 'keywords']
HEADER_LINE = 1

class Filter(object):
    cache:Cache
    config:Config

    def __init__(self, cache:Cache, config:Config):
        self.cache = cache
        self.config = config

    def filter(self, keywords:List[str]=[]) -> Optional[str]:
        """Spwan a interactive filter and return selected ID"""

        # Spwan filter
        args = self.config.filter(COLUMNS, HEADER_LINE, keywords)
        p = subprocess.Popen(['sh', '-c', ' '.join(args)],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

        # Calcuate width
        term_width = shutil.get_terminal_size((120, 0)).columns
        term_width -= 2 # Filter border
        excerpt_width = int(term_width * 3 / 4)
        path_width = int(term_width * 1 / 4)
        path_comp_width = path_width // 3

        # Write header
        from .utils import ellipsis
        header = '%s  %s  %s  %s\n' % (
            'ID',
            ellipsis.ellipsis('Excerpt', excerpt_width, blank_sym=' '),
            ellipsis.ellipsis('Path', path_width, blank_sym=' ' ),
            'Keywords')
        try:
            p.stdin.write(header.encode('utf-8'))
        except KeyboardInterrupt:
            return

        # Write rows
        for index in self.cache.indexes.values():
            row = '%s  %s  %s  %s\n' % (
                index[0], # ID
                ellipsis.ellipsis(index[1], excerpt_width, blank_sym=' '), # Excerpt
                ellipsis.join(index[2], path_width, path_comp_width, blank_sym=' ' ), # Titleppath
                ','.join(index[3])) # Keywords
            try:
                p.stdin.write(row.encode('utf-8'))
                p.stdin.flush()
            except KeyboardInterrupt:
                return

        try:
            p.stdin.close()
            p.wait()
        except KeyboardInterrupt:
            return

        if p.returncode == 0: # Normally exited
            stdout = p.stdout.read().decode('utf-8').strip().replace('\n', '')
            return stdout.split(' ')[0] # Return snippet ID
        elif p.returncode == 130: # Terminated by Control-C
            return None
        else:
            raise('filter exited with code %s:%s' % (
                p.returncode, p.stderr.read().decode('utf-8')))


    def view(self, uid:str) -> None:
        args = self.config.viewer(self.cache.previewfile(uid))
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            return


    def edit(self, uid:str) -> None:
        snippet = self.cache[uid].snippet
        args = self.config.editor(snippet.source(), line=snippet.scopes()[0][0])
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            return
