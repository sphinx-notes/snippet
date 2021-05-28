"""
    sphinxnotes.utils.ellipsis
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utils for ellipsis string.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List
from wcwidth import wcswidth

def ellipsis(text:str, width:int, ellipsis_sym:str='..', blank_sym:str=None) -> str:
    text_width = wcswidth(text)
    if text_width <= width:
        if blank_sym:
            # Padding with blank_sym
            text += blank_sym * ((width - text_width)//wcswidth(blank_sym))
        return text
    width -= wcswidth(ellipsis_sym)
    if width > text_width:
        width = text_width
    i = 0
    new_text = ''
    while wcswidth(new_text) < width:
        new_text += text[i]
        i += 1
    return new_text + ellipsis_sym


def join(lst:List[str], total_width:int, title_width:int,
         separate_sym:str='/', ellipsis_sym:str='..', blank_sym:str=None):
    # TODO: position
    total_width -= wcswidth(ellipsis_sym)
    result = []
    for i, l in enumerate(lst):
        l = ellipsis(l, title_width, ellipsis_sym=ellipsis_sym, blank_sym=None)
        l_width = wcswidth(l) + (wcswidth(separate_sym) if i != 0 else 0)
        if total_width - l_width < 0:
            break
        result.append(l)
        total_width -= l_width
    s = separate_sym.join(result)
    if blank_sym:
        s += blank_sym * (total_width // wcswidth(blank_sym))
    return s
