"""
    sphinxnotes.snippet.picker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet picker(node visitor) implementations.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from docutils import nodes

if TYPE_CHECKING:
    from sphinx.builders import Builder
from sphinx.util.docutils import SphinxTranslator

from . import Code, next_sibling_node

class CodePicker(SphinxTranslator):
    """Node visitor for picking code snippet from document."""
    # TODO: term support

    # Code snippets picked from document
    snippets:List[Code]

    # Stack of Structural node
    _stack:List[nodes.Structural]
    _cur_title:nodes.title
    _cur_ptr:nodes.Node


    def __init__(self, document:nodes.document, builder:Builder) -> None:
        super().__init__(document, builder)

        self._stack = []
        self._cur_title = None
        self._cur_ptr = None

        self.snippets = []


    def visit_Structural(self, node:nodes.Structural) -> None:
        self._stack.append(node)


    def depart_Structural(self, node:nodes.Structural) -> None:
        self._stack.pop()


    def visit_title(self, node:nodes.title) -> None:
        self._cur_title = node
        self._cur_ptr = next_sibling_node(node)


    def visit_literal_block(self, node:nodes.literal_block) -> None:
        # Find code container that has same level as self._cur_ptr
        container = node
        while container.parent not in [self._stack[-1], None]:
            container = container.parent

        desc = []
        if self._cur_ptr:
            for n in self._cur_ptr.traverse(include_self=True, descend=False, siblings=True, ascend=False):
                if n == container:
                    break
                desc.append(n)
        self.snippets.append(Code(self._cur_title, desc, node))
        self._cur_ptr = next_sibling_node(container)


    def unknown_visit(self, node:nodes.Node) -> None:
        # Ignore any unknown node
        pass


    def unknown_departure(self, node:nodes.Node) -> None:
        # Ignore any unknown node
        pass
