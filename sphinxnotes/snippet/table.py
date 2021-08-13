"""
    sphinxnotes.snippet.table
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Iterator, Dict

from .cache import Index, IndexID
from .utils import ellipsis

COLUMNS = ['id', 'tags', 'excerpt', 'path', 'keywords']
VISIABLE_COLUMNS = COLUMNS[1:4]
COLUMN_DELIMITER = '  '

def tablify(indexes: Dict[IndexID,Index], tags:str, width:int) -> Iterator[str]:
    """ Create a table from sequence of cache.Index. """

    # Calcuate width
    width = width
    tags_width = len(VISIABLE_COLUMNS[0])
    width -= tags_width
    excerpt_width = max(int(width * 6/10), len(VISIABLE_COLUMNS[1]))
    path_width = max(int(width * 4/10), len(VISIABLE_COLUMNS[2]))
    path_comp_width = path_width // 3

    # Write header
    header = COLUMN_DELIMITER.join(
        [COLUMNS[0].upper(),
         ellipsis.ellipsis(COLUMNS[1].upper(), tags_width, blank_sym=' '),
         ellipsis.ellipsis(COLUMNS[2].upper(), excerpt_width, blank_sym=' '),
         ellipsis.ellipsis(COLUMNS[3].upper(), path_width, blank_sym=' ' ),
         COLUMNS[4].upper()])
    yield header

    # Write rows
    for index_id, index in indexes.items():
        # TODO: assert index?
        if index[0] not in tags and '*' not in tags:
            continue
        row = COLUMN_DELIMITER.join(
            [index_id, # ID
             ellipsis.ellipsis(f'[{index[0]}]', tags_width, blank_sym=' '), # Kind
             ellipsis.ellipsis(index[1], excerpt_width, blank_sym=' '), # Excerpt
             ellipsis.join(index[2], path_width, path_comp_width, blank_sym=' ' ), # Titleppath
             ','.join(index[3])]) # Keywords
        yield row
