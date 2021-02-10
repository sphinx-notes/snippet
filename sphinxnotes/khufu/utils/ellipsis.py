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

def ellipsis(text:str, width:int, placeholder:str='...'):
    if wcswidth(text) <= width:
        return text
    width -= wcswidth(placeholder)
    if width > wcswidth(text):
        width = wcswidth(text)
    i = 0
    new_text = ''
    while wcswidth(new_text) < width:
        new_text += text[i]
        i += 1
    return new_text + placeholder


def join(l:List[str], total_width:int, title_width:int,
         separator:str='/', placeholder:str='...'):
    # TODO: position
    total_width -= wcswidth(placeholder)
    result = []
    for s in l:
        result.append(ellipsis(s, title_width, placeholder=placeholder))
        if wcswidth(separator.join(result)) > total_width:
            result.append(placeholder)
            break
    return separator.join(result)
