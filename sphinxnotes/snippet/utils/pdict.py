"""
    sphinxnotes.utils.pdict
    ~~~~~~~~~~~~~~~~~~~~~~~

    A customized persistent KV store for Sphinx project.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
from typing import Dict, Optional, Iterable, TypeVar
import pickle
from collections.abc import MutableMapping
from hashlib import sha1

K = TypeVar('K')
V = TypeVar('V')

# FIXME: PDict is buggy
class PDict(MutableMapping):
    """A persistent dict with event handlers."""

    dirname:str
    # The real in memory store of values
    _store:Dict[K,V]
    # Items that need write back to store
    _dirty_items:Dict[K,V]
    # Items that need purge from store
    _orphan_items:Dict[K,V]


    def __init__(self, dirname:str) -> None:
        self.dirname = dirname
        self._store = {}
        self._dirty_items = {}
        self._orphan_items = {}


    def __getitem__(self, key:K) -> Optional[V]:
        if not key in self._store:
            raise KeyError
        value = self._store[key]
        if value is not None:
            return value
        # V haven't loaded yet, load it from disk
        with open(self.itemfile(key), 'rb') as f:
            value = pickle.load(f)
            self._store[key] = value
            return value


    def __setitem__(self, key:K, value:V) -> None:
        assert value is not None
        if key in self._store:
            self.__delitem__(key)
        self._dirty_items[key] = value
        self._store[key] = value


    def __delitem__(self, key:K) -> None:
        value = self.__getitem__(key)
        del self._store[key]
        if key in self._dirty_items:
            del self._dirty_items[key]
        else:
            self._orphan_items[key] = value


    def __iter__(self) -> Iterable:
        return iter(self._store)


    def __len__(self) -> int:
        return len(self._store)


    def _keytransform(self, key:K) -> K:
        # No used
        return key


    def load(self) -> None:
        with open(self.dictfile(), 'rb') as f:
            obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)


    def dump(self):
        """Dump store to disk."""
        from sphinx.util import status_iterator

        # Makesure dir exists
        if not path.exists(self.dirname):
            os.makedirs(self.dirname)

        # Purge orphan items
        for key, value in status_iterator(self._orphan_items.items(),
                                          'purging orphan document(s)... ',
                                          'brown', len(self._orphan_items), 0,
                                          stringify_func=lambda i: self.stringify(i[0], i[1])):
            os.remove(self.itemfile(key))
            self.post_purge(key, value)

        # Dump dirty items
        for key, value in status_iterator(self._dirty_items.items(),
                                          'dumping dirty document(s)... ',
                                          'brown', len(self._dirty_items), 0,
                                          stringify_func=lambda i: self.stringify(i[0], i[1])):
            with open(self.itemfile(key), 'wb') as f:
                pickle.dump(value, f)
            self.post_dump(key, value)

        # Clear all in-memory items
        self._orphan_items = {}
        self._dirty_items = {}
        self._store = {key: None for key in self._store}

        # Dump store itself
        with open(self.dictfile(), 'wb') as f:
            pickle.dump(self, f)


    def dictfile(self) -> str:
        return path.join(self.dirname, 'dict.pickle')


    def itemfile(self, key:K) -> str:
        hasher = sha1()
        hasher.update(pickle.dumps(key))
        return path.join(self.dirname, hasher.hexdigest()[:7] + '.pickle')


    def post_dump(self, key:K, value:V) -> None:
        pass


    def post_purge(self, key:K, value:V) -> None:
        pass


    def stringify(self, key:K, value:V) -> str:
        return key
