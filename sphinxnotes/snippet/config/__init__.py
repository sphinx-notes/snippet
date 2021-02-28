"""
    sphinxnotes.snippet.config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Dict, Any

from . import default

class Config(object):
    """Snippet configuration object."""

    def __init__(self, config:Dict[str,Any]) -> None:
        # Load default
        self.__dict__.update(default.__dict__)
        for name in config:
            if name.startswith('__') and name != '__file__':
                # Ignore unrelated name
                continue
            if name in self.__dict__.keys():
                self.__dict__[name] = config[name]


    @classmethod
    def load(cls, filename:str) -> "Config":
        """Load config from configuration file"""
        with open(filename, 'rb') as f:
            source = f.read()
        # Compile to a code object
        code = compile(source, filename, 'exec')
        config = {'__file__': filename}
        # Compile to a code object
        exec(code, config)
        return cls(config)
