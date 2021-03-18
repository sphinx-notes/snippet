""" sphinxnotes.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Dict
from dataclasses import dataclass

from . import Snippet
from .utils.pdict import PDict

@dataclass(frozen=True)
class Item(object):
    """ Item of snippet cache. """
    snippet:Snippet
    titlepath:List[str]
    keywords:List[Tuple[str,float]] # (Keywords, Rank)

DocID = Tuple[str, str] # (project, docname)
ItemList = List[Item]
ItemID = Tuple[DocID,int]
Index = Tuple[str,str,List[str],List[str]] # (kind, excerpt, titlepath, keywords)

class Cache(PDict):
    """A DocID -> ItemList Cache."""
    indexes:Dict[ItemID,Index] # Table of index

    def __init__(self, dirname:str) -> None:
        self.indexes = {}
        super().__init__(dirname)


    def post_dump(self, key:DocID, items:ItemList) -> None:
        """Overwrite PDict.post_dump."""
        # Update items index
        for i, item in enumerate(items):
            self.indexes[(key, i)] = (
                item.snippet.kind(),
                item.snippet.excerpt(),
                item.titlepath,
                [keyword for keyword, rank in item.keywords])


    def post_purge(self, key:DocID, items:ItemList) -> None:
        """Overwrite PDict.post_purge."""
        for i, _ in enumerate(items):
            del self.indexes[(key, i)]


    def stringify(self, key:DocID, items:ItemList) -> str:
        """Overwrite PDict.stringify."""
        return key[1]
