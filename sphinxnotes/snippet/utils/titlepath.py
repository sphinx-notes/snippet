"""
    sphinxnotes.utils.titlepath
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utils for ellipsis string.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""
from __future__ import annotations
from typing import List, Optional, Tuple, TYPE_CHECKING

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.enviornment import BuilderEnviornment


def safe_descend(node:nodes.Node, *args: int) -> Optional[nodes.Node]:
    try:
        for index in args:
            node = node[index]
        return node
    except:
        return None


def resolve_fullpath(env: BuilderEnviornment, doctree:nodes.document,
                     docname:str, node:nodes.Node) -> List[str]:
    return [x.astext() for x in resolve_sectpath(doctree, node)] + \
        resolve_docpath(env, docname)


def resolve_sectpath(doctree:nodes.document, node:nodes.Node) -> List[nodes.title]:
    # FIXME: doc is None
    _, subtitlenode = resolve_doctitle(doctree)
    titlenodes = []
    while node:
        secttitle = resolve_secttitle(node)
        node = node.parent
        if not secttitle or secttitle == subtitlenode:
            continue
        titlenodes.append(secttitle)
    return titlenodes


def resolve_secttitle(node:nodes.Node) -> Optional[nodes.title]:
    titlenode = safe_descend(node.parent, 0)
    if not isinstance(titlenode, nodes.title):
        return None
    return titlenode


def resolve_docpath(env:BuilderEnviornment, docname:str) -> List[str]:
    titles = []
    master_doc = env.config.master_doc
    v = docname.split('/')
    if v.pop() == master_doc:
        if v:
            # If docname is "a/b/index", we need titles of "a"
            v.pop()
        else:
            # docname is "index", no need to get docpath, it is root doc
            return []
    while v:
        master_docname = '/'.join(v + [master_doc])
        if master_docname in env.titles:
            title = env.titles[master_docname].astext()
        else:
            title = v[-1].title()
        titles.append(title)
        v.pop()
    titles.reverse()
    return titles


def resolve_doctitle(doctree:nodes.document) -> Tuple[Optional[nodes.title],
                                                          Optional[nodes.title]]:

    toplevel_sectnode = doctree.next_node(nodes.section)
    if not toplevel_sectnode:
        return (None, None)

    titlenode = safe_descend(toplevel_sectnode, 0)
    # NOTE: nodes.subtitle does not make senses beacuse Sphinx doesn't support
    # subtitle:
    #
    # > Sphinx does not support a "subtitle".
    # > Sphinx recognizes it as a mere second level section
    #
    # ref:
    # - https://github.com/sphinx-doc/sphinx/issues/3574#issuecomment-288722585
    # - https://github.com/sphinx-doc/sphinx/issues/3567#issuecomment-288093991
    if len(toplevel_sectnode) != 2:
        return (titlenode, None)
    # HACK: For our convenience, we regard second level section title
    # (under document) as subtitle::
    # <section>
    #   <title>
    #   <section>
    #       <(sub)title>
    subtitlenode = toplevel_sectnode[1][0]
    if not isinstance(subtitlenode, nodes.title):
        return (titlenode, None)
    return (titlenode, subtitlenode)
