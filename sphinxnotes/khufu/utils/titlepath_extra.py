"""
    sphinxnotes.utils.titlepath_extra
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for titlepath module.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import List

from wcwidth import wcswidth

def shorten(text:str, width:int, placeholder:str):
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


def join(titlepath:List[str], total_width:int, title_width:int,
                       separator:str='/', placeholder:str='...'):
    # TODO: position
    total_width -= wcswidth(placeholder)
    result = []
    titlepath.reverse()
    for title in titlepath:
        result.append(shorten(title, title_width, placeholder))
        if wcswidth(separator.join(result)) > total_width:
            break
    result.append(placeholder)
    result.reverse()
    return separator.join(result)
