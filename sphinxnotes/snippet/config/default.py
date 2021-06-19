"""
    sphinxnotes.snippet.config.default
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet default configuration.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

# NOTE: All imported name should starts with ``__`` to distinguish from
# configuration item
from os import path as __path
from xdg.BaseDirectory import xdg_cache_home as __xdg_cache_home
from .. import __title__

"""
``cache_dir``
    (Type: ``str``)
    (Default: ``"$XDG_CACHE_HOME/sphinxnotes/snippet"``)
    Path to snippet cache directory.
"""
cache_dir = __path.join(__xdg_cache_home, *__title__.split('-'))

"""
``base_urls``
    (Type: ``Dict[str,str]``)
    (Default: ``{}``)
    A "project name" -> "base URL" mapping.
    Base URL is used to generate snippet URL.
"""
base_urls = {}
