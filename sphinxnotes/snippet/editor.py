"""
    sphinxnotes.snippet.editor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet editor wrapper.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import subprocess

from . import Snippet
from .config import Config

class Editor(object):
    config:Config

    def __init__(self, config:Config):
        self.config = config

    def edit(self, snippet:Snippet) -> None:
        args = self.config.editor(snippet.source(), line=snippet.scopes()[0][0])
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            return
