""" sphinxnotes.khufu.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
from typing import List, Tuple, Dict
from dataclasses import dataclass
import pickle

# from rst2ansi import rst2ansi

from .import Snippet, Notes


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
        [hasher.update(line.encode()) for line in self.snippet.rst()]
        [hasher.update(keyword.encode()) for keyword, _ in self.keywords]
        return hasher.hexdigest()

class Cache(object):
    """Cache of snippet."""
    # Path to directory for saving cache
    dirname:str
    # Items that need write back to disk
    _dirty_items:Dict[str,Item]
    # Persistent items that loads from disk (hexdigest -> Item)
    _persistent_items:Dict[str,Item]

    def __init__(self, dirname:str) -> None:
        self.dirname = dirname
        self._dirty_items = {}
        self._persistent_items = {}


    def cachefile(self) -> str:
        return path.join(self.dirname, 'cache.pickle')


    def indexfile(self) -> str:
        return path.join(self.dirname, 'index.txt')


    def snippetfile(self, uid:str) -> str:
        return path.join(self.dirname, uid + '.rst')


    def add(self, item:Item) -> str:
        """Add item to cache, return ID of item"""
        digest = item.hexdigest()
        self._dirty_items[digest] = item
        return digest


    def get(self, uid:str) -> Item:
        return self._persistent_items.get(uid)


    def items(self) -> List[Tuple[str,Item]]:
        return self._persistent_items.items()


    def purge(self, project, docname:str) -> int:
        """Pure persistent items that belongs to given docname. """
        uids = []
        for uid, item in self._persistent_items:
            if item.project == project and item.docname == docname:
                uids.append(uid)
        for uid in uids:
            self._del_item(uid)
        return len(uids)


    def load(self) -> None:
        with open(self.cachefile(), 'rb') as f:
            obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)


    def dump(self) -> None:
        """Save cache to directory."""
        # Makesure dir exists
        if not path.exists(self.dirname):
            os.mkdir(self.dirname)

        # Merge items
        self._merge_items()

        # Dump indexes
        with open(self.indexfile(), 'w') as f:
            f.write(self._dump_indexes())

        # Dump self
        with open(self.cachefile(), 'wb') as f:
            pickle.dump(self, f)


    def _dump_indexes(self) -> str:
        from ..utils.titlepath_extra import join
        ELLIPSIS = '…'
        lines = []
        for uid, item in self._persistent_items.items():
            titlepath = join(item.titlepath, 30, 15, placeholder=ELLIPSIS)
            if isinstance(item.snippet, Notes):
                excerpt = item.snippet.excerpt()
            else:
                excerpt = '<no excerpt available>'
            keywords = [keyword for keyword, rank in item.keywords]
            lines.append([uid, titlepath, excerpt, ','.join(keywords)])
        from tabulate import tabulate
        return tabulate(lines, headers=['ID', 'Path', 'Excerpt', 'Keywords'], tablefmt='plain')


    def _del_item(self, uid:str) -> int:
        del self._persistent_items[uid]
        os.remove(self.snippetfile(uid))


    def _dump_item(self, uid:str, item:Item) -> None:
        # TODO: fix rst2ansi
        # with open(path.join(dirname, uid+ '.ansi'), 'w') as f:
        #   f.write('\n'.join(rst2ansi(item.snippet.rst())))
        with open(self.snippetfile(uid), 'w') as f:
            f.write('\n'.join(item.snippet.rst()))


    def _merge_items(self) -> None:
        # Detect deletetd snippets in persistent items
        #
        # "Deleted" means: Documentation changed but the previous snippet is
        # not ``add`` again.
        ndel = 0
        docnames = set([(item.project, item.docname) for _, item in self._dirty_items.items()])
        for uid, item in self._persistent_items:
            if not (item.project, item.docname) in docnames:
                self._del_item(uid)
                ndel +=1

        nadd = 0
        # Merge dirty items
        for uid, item in self._dirty_items.items():
            if uid not in self._persistent_items:
                # Dirty items is new item
                self._persistent_items[uid] = item
                self._dump_item(uid, item)
                nadd +=1

        print('%d documentation(s) changed, %d snippet(s) deleted and %d snippet(s) added' % (len(docnames), ndel, nadd))

