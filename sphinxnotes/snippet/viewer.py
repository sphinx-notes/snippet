"""
    sphinxnotes.snippet.viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet viewer wrapper.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import subprocess
from tempfile import NamedTemporaryFile

from . import Snippet
from .config import Config

class Viewer(object):
    config:Config

    def __init__(self, config:Config):
        self.config = config

    def view(self, snippet:Snippet) -> None:
        # FIXME: use snippet.source() for Headline
        with NamedTemporaryFile(mode='w') as f:
            for l in snippet.original():
                f.write(l)
                f.write('\n')
            args = self.config.viewer(f.name)
            try:
                f.flush()
                subprocess.run(args)
            except KeyboardInterrupt:
                return
