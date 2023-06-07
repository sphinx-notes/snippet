""" sphinxnotes.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

from . import Snippet
from .utils.pdict import PDict

@dataclass(frozen=True)
class Item(object):
    """ Item of snippet cache. """
    snippet:Snippet
    tags:List[str]
    excerpt:str
    titlepath:List[str]
    keywords:List[str]


DocID = Tuple[str,str] # (project, docname)
IndexID = str # UUID
Index = Tuple[str,str,List[str],List[str]] # (tags, excerpt, titlepath, keywords)

class Cache(PDict):
    """A DocID -> List[Item] Cache."""
    indexes:Dict[IndexID,Index]
    index_id_to_doc_id:Dict[IndexID,Tuple[DocID,int]]
    doc_id_to_index_ids:Dict[DocID,List[IndexID]]
    num_snippets_by_project:Dict[str,int]
    num_snippets_by_docid:Dict[DocID,int]

    def __init__(self, dirname:str) -> None:
        self.indexes = {}
        self.index_id_to_doc_id = {}
        self.doc_id_to_index_ids = {}
        self.num_snippets_by_project= {}
        self.num_snippets_by_docid = {}
        super().__init__(dirname)


    def post_dump(self, key:DocID, items:List[Item]) -> None:
        """Overwrite PDict.post_dump."""

        # Remove old indexes and index IDs if exists
        for old_index_id in self.doc_id_to_index_ids.setdefault(key, []):
            del self.index_id_to_doc_id[old_index_id]
            del self.indexes[old_index_id]

        # Add new index to every where
        for i, item in enumerate(items):
            index_id = self.gen_index_id()
            self.indexes[index_id] = (item.tags,
                                      item.excerpt,
                                      item.titlepath,
                                      item.keywords)
            self.index_id_to_doc_id[index_id] = (key, i)
            self.doc_id_to_index_ids[key].append(index_id)

        # Update statistic
        if key[0] not in self.num_snippets_by_project:
            self.num_snippets_by_project[key[0]] = 0
        self.num_snippets_by_project[key[0]] += len(items)
        if key not in self.num_snippets_by_docid:
            self.num_snippets_by_docid[key] = 0
        self.num_snippets_by_docid[key] += len(items)


    def post_purge(self, key:DocID, items:List[Item]) -> None:
        """Overwrite PDict.post_purge."""

        # Purge indexes
        for index_id in self.doc_id_to_index_ids.pop(key):
            del self.index_id_to_doc_id[index_id]
            del self.indexes[index_id]

        # Update statistic
        self.num_snippets_by_project[key[0]] -= len(items)
        if self.num_snippets_by_project[key[0]] == 0:
            del self.num_snippets_by_project[key[0]]
        self.num_snippets_by_docid[key] -= len(items)
        if self.num_snippets_by_docid[key] == 0:
            del self.num_snippets_by_docid[key]


    def get_by_index_id(self, key:IndexID) -> Optional[Item]:
        """Like get(), but use IndexID as key."""
        doc_id, item_index = self.index_id_to_doc_id.get(key, (None,None))
        if not doc_id:
            return None
        return self[doc_id][item_index]


    def gen_index_id(self) -> str:
        """Generate unique ID for index."""
        import uuid
        return uuid.uuid4().hex[:7]


    def stringify(self, key:DocID, items:List[Item]) -> str:
        """Overwrite PDict.stringify."""
        return key[1]
