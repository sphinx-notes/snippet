""" sphinxnotes.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
from typing import List, Tuple
from dataclasses import dataclass

from . import Snippet
from .utils.docmapping import Mapping


@dataclass(frozen=True)
class Item(object):
    """ Item of snippet cache. """
    # Name of sphinx project
    project:str # TODO
    # Name of documentation
    docname:str
    titlepath:List[str]
    snippet:Snippet
    # (Keywords, Rank)
    keywords:List[Tuple[str,float]]

    def hexdigest(self) -> str:
        from hashlib import sha1
        hasher = sha1()
        # TODO: none for now
        if self.project:
            hasher.update(self.project.encode())
        hasher.update(self.docname.encode())
        [hasher.update(title.encode()) for title in self.titlepath]
        [hasher.update(line.encode()) for line in self.snippet.original()]
        [hasher.update(keyword.encode()) for keyword, _ in self.keywords]
        return hasher.hexdigest()


class Cache(Mapping):
    """Cache of snippet."""
    # Table of index: ID, excerpt, titlepath, keywords
    indexes:Tuple[str,str,List[str],List[str]]

    def __init__(self, dirname:str) -> None:
        self.indexes = {}
        super().__init__(dirname)


    def post_dump_item(self, key:str,item:Item) -> None:
        """Overwrite Mapping.post_dump."""

        # Update item index
        excerpt = item.snippet.excerpt()
        keywords = [keyword for keyword, rank in item.keywords]
        self.indexes[key] = (key, excerpt, item.titlepath, keywords)

        # Update item preview
        with open(self.previewfile(key), 'w') as f:
            f.write('\n'.join(item.snippet.original()))


    def post_purge_item(self, key:str, item:Item) -> None:
        """Overwrite Mapping.post_purge."""
        del self.indexes[key]
        os.remove(self.previewfile(key))


    def previewfile(self, key:str) -> str:
        return path.join(self.dirname, key + '.rst')


    def add(self, item:Item) -> str:
        """Add item to cache, return ID of item"""
        digest = item.hexdigest()[:7]
        self[digest] = item
        return digest


    def purge_doc(self, project:str, docname:str) -> None:
        """Pure persistent items that belongs to given docname. """
        for k in self.by_docname(project, docname):
            del self[k]
