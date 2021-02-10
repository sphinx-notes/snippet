"""
    sphinxnotes.utils.titlepath
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utils for ellipsis string.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.builders import Builder


class Resolver(object):
    _builder:Builder

    def __init__(self, builder: Builder) -> None:
        self._builder = builder


    def resolve(self, docname:str, node:nodes.Node,
                include_docpath:bool=True) -> List[str]:
        titles = []
        while node.parent:
            node = node.parent
            titlenode = node.next_node(condition=self._title_node_filter)
            if not titlenode or titlenode.parent != node:
                # No title node or title node is not direct child
                continue
            titles.append(titlenode.astext())
        if include_docpath:
            titles += self.resolve_docpath(docname)
        return titles


    def resolve_docpath(self, docname:str) -> List[str]:
        titles = []
        master_doc = self._builder.config.master_doc
        v = docname.split('/')
        if v.pop() == master_doc:
            if v:
                # If docname is "a/b/index", we need titles of "a"
                v.pop()
            else:
                # docname is "index", no need to get docpath, it is root doc
                return []
        while v:
            titles.append(self.resolve_doctitle('/'.join(v + [master_doc])) or \
                          v[-1].title())
            v.pop()
        titles.reverse()
        return titles


    def resolve_doctitle(self, docname:str) -> Optional[str]:
        if docname in self._builder.env.titles:
            return self._builder.env.titles[docname].astext()


    def _title_node_filter(self, node:nodes.Node) -> bool:
        if not isinstance(node, nodes.title):
            return False
        # NOTE: ``isinstance(node, nodes.subtitle)`` does not make senses
        # beacuse Sphinx doesn't support subtitle:
        #
        # > Sphinx does not support a "subtitle".
        # > Sphinx recognizes it as a mere second level section
        #
        # ref:
        # - https://github.com/sphinx-doc/sphinx/issues/3574#issuecomment-288722585
        # - https://github.com/sphinx-doc/sphinx/issues/3567#issuecomment-288093991
        if isinstance(node, nodes.subtitle):
            return False
        # HACK: For our convenience, we regard second level section title
        # (under document) as subtitle
        if not node.document:
            # FIXME: I don't know why there is a None document, fix it
            return True
        toplevel_section = node.document.next_node(nodes.section)
        if node.parent.parent == toplevel_section and len(toplevel_section) == 2:
            # Second level secion under toplevel section
            # AND
            # Top level section and only 2 child: its title and second level section
            # THEN we regard it as subtitle
            return False
        return True
