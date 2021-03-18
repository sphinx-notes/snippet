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
import tempfile

from .cache import Cache, Item, ItemID
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

    def filter(self, keywords:List[str]=[], kinds:str='*') -> Optional[Item]:
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
        header = COLUMN_DELIMITER.join(
            [COLUMNS[0].upper(),
             ellipsis.ellipsis(COLUMNS[1].upper(), kind_width, blank_sym=' '),
             ellipsis.ellipsis(COLUMNS[2].upper(), excerpt_width, blank_sym=' '),
             ellipsis.ellipsis(COLUMNS[3].upper(), path_width, blank_sym=' ' ),
             COLUMNS[4].upper()]) + '\n'
        try:
            p.stdin.write(header.encode('utf-8'))
        except KeyboardInterrupt:
            return

        # Write rows
        row_id = 0
        item_ids = []
        for item_id, index in self.cache.indexes.items():
            if index[0] not in kinds and '*' not in kinds:
                continue
            row = COLUMN_DELIMITER.join(
                [str(row_id), # ID
                 ellipsis.ellipsis(f'[{index[0]}]', kind_width, blank_sym=' '), # Kind
                 ellipsis.ellipsis(index[1], excerpt_width, blank_sym=' '), # Excerpt
                 ellipsis.join(index[2], path_width, path_comp_width, blank_sym=' ' ), # Titleppath
                 ','.join(index[3])]) + '\n' # Keywords
            row_id += 1
            item_ids.append(item_id)
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
        if p.returncode == 130: # Terminated by Control-C
            return None
        elif p.returncode != 0:
            raise('filter exited with code %s:%s' % (
                p.returncode, p.stderr.read().decode('utf-8')))

        # Normally exited pass
        stdout = p.stdout.read().decode('utf-8').strip().replace('\n', '')
        row_id = int(stdout.split('  ')[0])
        item_id = item_ids[row_id]
        doc_id, item_offset = item_id
        return self.cache[doc_id][item_offset]


    def view(self, id:ItemID) -> None:
        doc_id, item_offset = id
        snippet = self.cache[doc_id][item_offset].snippet
        # FIXME
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(snippet.original())
        args = self.config.viewer(snippet.original())
        return
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            return


    def edit(self, id:ItemID) -> None:
        doc_id, item_offset = id
        snippet = self.cache[doc_id][item_offset].snippet
        args = self.config.editor(snippet.source(), line=snippet.scopes()[0][0])
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            return
