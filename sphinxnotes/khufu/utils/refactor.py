"""
    sphinxnotes.utils.refactor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import Set
from enum import Enum, auto

class Feature(Enum):
    fetch_url_title = auto()
    mark_bad_url = auto()
    generate_title_target = auto()
    eliminate_inline_markup_surrounding_spaces = auto()

class Refactor(object):
    def __init__(feats:Set[Feature]):
        pass
