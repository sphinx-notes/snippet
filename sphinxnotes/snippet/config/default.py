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
from . import preset as __preset
from .. import __title__


"""
``cache_dir``
    (Default: ``"$XDG_CACHE_HOME/sphinxnotes-snippet"``)
    Path to snippet cache directory.
"""
cache_dir = __path.join(__xdg_cache_home, __title__)


"""
``filter``
    (Default: ``sphinxnotes.snippet.config.preset.fzf_filter``)
    Callable object for generating command for filtering snippet.

    Filter should be a interactive selector that supports keyword search,
    such as Fzf, Fzy, Skim.

    If you want to write your own one, please refer to package
    `sphinxnotes.snippet.config.preset`
"""
filter = __preset.fzf_filter


"""
``viewer``
    (Default: ``sphinxnotes.snippet.config.preset.cat_viewer``)
    Callable object for generating command for viewing snippet.

    Viewer should be a plain text document reader at least, like cat and less.

    If you want to write your own one, please refer to package
    `sphinxnotes.snippet.config.preset`
"""
viewer = __preset.cat_viewer


"""
``editor``
    (Default: ``sphinxnotes.snippet.config.preset.vim_editor``)
    Callable object for generating command for editing snippet.

    Viewer should be a text editor at least, such as nano, vim, emacs and so on.

    If you want to write your own one, please refer to package
    `sphinxnotes.snippet.config.preset`
"""
editor = __preset.vim_editor
