"""
sphinxnotes.utils.titlepath
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utils for ellipsis string.

:copyright: Copyright 2020 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment


def resolve(
    env: BuildEnvironment, docname: str, node: nodes.Element
) -> list[nodes.title]:
    return resolve_section(node) + resolve_document(env, docname)


def resolve_section(node: nodes.Element) -> list[nodes.title]:
    titlenodes = []
    while node:
        if len(node) > 0 and isinstance(node[0], nodes.title):
            titlenodes.append(node[0])
        node = node.parent
    return titlenodes


def resolve_document(env: BuildEnvironment, docname: str) -> list[nodes.title]:
    """NOTE: Title of document itself does not included in the returned list"""
    titles = []
    master_doc = env.config.master_doc
    v = docname.split('/')

    # Exclude self
    if v.pop() == master_doc and v:
        # If self is master_doc, like: "a/b/c/index", we only return titles
        # of "a/b/", so pop again
        v.pop()

    # Collect master doc title in docname
    while v:
        master_docname = '/'.join(v + [master_doc])
        if master_docname in env.titles:
            title = env.titles[master_docname]
        else:
            title = nodes.title(text=v[-1].title())  # FIXME: Create mock title for now
        titles.append(title)
        v.pop()

    # Include title of top-level master doc
    if master_doc in env.titles:
        titles.append(env.titles[master_doc])

    return titles
