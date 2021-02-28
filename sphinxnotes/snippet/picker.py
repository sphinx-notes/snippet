"""
    sphinxnotes.snippet.picker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet picker implementations.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Optional, Dict

from docutils import nodes

from . import Headline, Code, Procedure
from .utils.titlepath import resolve_doctitle


def pick_doctitle(doctree:nodes.document) -> Optional[Headline]:
    """Pick document title and subtitle (if have) from document."""
    title, subtitle = resolve_doctitle(doctree)
    if not title:
        return None
    return Headline(title=title, subtitle=subtitle)


def pick_codes(doctree:nodes.document) -> List[Code]:
    """Pick code snippet from document."""
    picker = CodePicker(doctree)
    doctree.walkabout(picker)
    return picker.codes


class CodePicker(nodes.SparseNodeVisitor):
    """Node visitor for picking code snippet from document."""
    # Code snippets that picked from document
    codes:List[Code]
    # Procedures that picked from document, TODO
    procedures:List[Procedure]
    # (container, pointer) that Recording the read pointer inside container
    offset:Dict[nodes.Node,int]
    # List of unsupported languages (:class:`pygments.lexers.Lexer`)
    unsupported_languages:List[str] = ['default']


    def __init__(self, document:nodes.document) -> None:
        super().__init__(document)
        self.codes = []
        self.procedures = []
        self.offset = {}


    def visit_literal_block(self, node:nodes.literal_block) -> None:
        if node['language'] in self.unsupported_languages:
            raise nodes.SkipNode

        desc = []
        container = node.parent
        # Get current offset or use first child of container (must exists)
        start = self.offset.get(container) or 0
        # Stop iteration before current literal_block
        end = container.index(node)
        # Collect description
        for i in range(start, end):
            if self.is_description(container[i]):
                desc.append(container[i])
        i += 1 # Skip literal_block
        # Collect continuously post_description
        for i in range(i, len(container)):
            if self.is_post_description(container[i]):
                desc.append(container[i])
            else:
                i -= 1 # Currnet node is not post_description
                break
        i += 1 # Skip last post_description

        self.offset[container] = i
        if desc:
            # Only add code with description
            self.codes.append(Code(description=desc,
                                   block=node))


    def visit_enumerated_list(self, node:nodes.enumerated_list) -> None:
        pass

    def depart_enumerated_list(self, node:nodes.enumerated_list) -> None:
        pass


    def unknown_visit(self, node:nodes.Node) -> None:
        pass # Ignore any unknown node

    def unknown_departure(self, node:nodes.Node) -> None:
        pass # Ignore any unknown node


    def is_description(self, node:nodes.Node) -> bool:
        """Return whether given node can be description of code in :class:`Code` ."""
        return isinstance(node, (nodes.Admonition, nodes.Sequential,
                                 nodes.paragraph, nodes.field, nodes.option,
                                 nodes.line_block))


    def is_post_description(self, node:nodes.Node) -> bool:
        """Return whether the given node can be post_description of code in :class:`Notes`."""
        return isinstance(node, nodes.Admonition)
