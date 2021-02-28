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
import subprocess
import shutil

from .cache import Cache
from .config import Config

COLUMNS = ['id', 'kind', 'excerpt', 'path', 'keywords']
VISIABLE_COLUMNS = COLUMNS[1:4]
COLUMN_DELIMITER = '  '
HEADER_LINE = 1

class Filter(object):
    cache:Cache
    config:Config

    def __init__(self, cache:Cache, config:Config):
        self.cache = cache
        self.config = config

    def filter(self, keywords:List[str]=[], kinds:str='*') -> Optional[str]:
        """Spwan a interactive filter and return selected ID"""

        # Spwan filter
        args = self.config.filter(COLUMNS, HEADER_LINE, keywords)
        p = subprocess.Popen(['sh', '-c', ' '.join(args)],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

        # Calcuate width
        term_width = shutil.get_terminal_size((120, 0)).columns
        term_width -= 2 # Filter border
        term_width -= len(VISIABLE_COLUMNS) * len(VISIABLE_COLUMNS) # Width of visiable columns
        kind_width = len(VISIABLE_COLUMNS[0])
        term_width -= kind_width
        excerpt_width = max(int(term_width * 6/10), len(VISIABLE_COLUMNS[1]))
        path_width = max(int(term_width * 4/10), len(VISIABLE_COLUMNS[2]))
        path_comp_width = path_width // 3

        # Write header
        from .utils import ellipsis
        header = '%s  %s  %s  %s  %s\n' % (
            'ID',
            ellipsis.ellipsis('Kind', kind_width, blank_sym=' '),
            ellipsis.ellipsis('Excerpt', excerpt_width, blank_sym=' '),
            ellipsis.ellipsis('Path', path_width, blank_sym=' ' ),
            'Keywords')
        try:
            p.stdin.write(header.encode('utf-8'))
        except KeyboardInterrupt:
            return

        # Write rows
        for index in self.cache.indexes.values():
            if index[1] not in kinds and '*' not in kinds:
                continue
            row = '%s  %s  %s  %s  %s\n' % (
                index[0], # ID
                ellipsis.ellipsis('[%s]' % index[1], kind_width, blank_sym=' '), # Kind
                ellipsis.ellipsis(index[2], excerpt_width, blank_sym=' '), # Excerpt
                ellipsis.join(index[3], path_width, path_comp_width, blank_sym=' ' ), # Titleppath
                ','.join(index[4])) # Keywords
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
