"""
    sphinxnotes.khufu.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

import os
from os import path
from typing import List, Tuple, Dict
from dataclasses import dataclass
import pickle
import uuid

from tabulate import tabulate
# from rst2ansi import rst2ansi

from ..utils.snippet import Snippet, Notes

@dataclass(frozen=True)
class Item(object):
    """ Item of snippet cache. """
    # Name of sphinx project
    projname:str # TODO
    # Name of documentation
    docname:str
    titlepath:List[str]
    snippet:Snippet
    # (Keywords, Rank)
    keywords:List[Tuple[str,float]]


class Cache(object):
    """Cache of snippet."""
    # UID -> Item
    _items: Dict[str,Item]

    def __init__(self) -> None:
        self._items = {}


    def add(self, item:Item) -> None:
        """Add item to cache."""
        uid = str(uuid.uuid4())[:8]
        self._items[uid] = item


    def get(self, uid:str) -> Item:
        return self._items.get(uid)


    def items(self) -> List[Tuple[str,Item]]:
        return self._items.items()


    def purge(self, docname:str) -> None:
        """Pure all items in given docname. """
        items = [(uid, item) for uid, item in self._items if item.docname == docname]
        for uid, item in items:
            del self._items[uid]
            # TODO: Del uid


    def dump(self, dirname:str) -> None:
        """Save cache to directory."""
        if not path.exists(dirname):
            os.mkdir(dirname)
        with open(path.join(dirname, 'cache.p'), 'wb') as f:
            pickle.dump(self, f)
        with open(path.join(dirname, 'index.txt'), 'w') as f:
            f.write(self._dump_indexes())
        # Dump snippet
        for uid, item in self.items():
            self._dump_item(dirname, uid, item)


    def _dump_indexes(self) -> str:
        ELLIPSIS = '…'
        lines = []
        for uid, item in self.items():
            titlepath = item.titlepath
            if len(titlepath) > 3:
                titlepath = [ELLIPSIS] + titlepath[-3:]
            if isinstance(item.snippet, Notes):
                excerpt = item.snippet.excerpt()
            else:
                excerpt = '<no excerpt available>'
            keywords = [keyword for keyword, rank in item.keywords]
            lines.append([uid, '/'.join(titlepath), excerpt, ','.join(keywords)])
        return tabulate(lines, headers=['ID', 'Path', 'Excerpt', 'Keywords'], tablefmt='plain')


    def _dump_item(self, dirname:str, uid:str, item:Item) -> None:
        with open(path.join(dirname, uid+ '.rst'), 'w') as f:
            f.write('\n'.join(item.snippet.rst()))
        # TODO: fix rst2ansi
        # with open(path.join(dirname, uid+ '.ansi'), 'w') as f:
        #   f.write('\n'.join(rst2ansi(item.snippet.rst())))
