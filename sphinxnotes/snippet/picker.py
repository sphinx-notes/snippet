"""
    sphinxnotes.snippet.picker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Snippet picker implementations.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple

from docutils import nodes

from sphinx.util import logging

from . import Snippet, Section, Document


logger = logging.getLogger(__name__)


def pick(doctree:nodes.document) -> List[Tuple[Snippet,nodes.section]]:
    """
    Pick snippets from document, return a list of snippet and the section
    it belongs to.
    """
    if doctree.source == "":
        logger.debug('Skipped document with empty source')
        return []

    snippets = []

    # Pick document
    toplevel_section = doctree.next_node(nodes.section)
    if toplevel_section:
        snippets.append((Document(doctree), toplevel_section))
    else:
        logger.warning('can not pick document without child section: %s', doctree)

    # Pick sections
    section_picker = SectionPicker(doctree)
    doctree.walkabout(section_picker)
    snippets.extend(section_picker.sections)

    return snippets


class SectionPicker(nodes.SparseNodeVisitor):
    """Node visitor for picking code snippet from document."""

    #: Constant list of unsupported languages (:class:`pygments.lexers.Lexer`)
    UNSUPPORTED_LANGUAGES:List[str] = ['default']

    #: List of picked section snippets and the section it belongs to
    sections:List[Tuple[Section,nodes.section]]

    _section_has_code_block:bool
    _section_level:int


    def __init__(self, document:nodes.document) -> None:
        super().__init__(document)
        self.sections = []
        self._section_has_code_block = False
        self._section_level = 0

    ###################
    # Visitor methods #
    ###################

    def visit_literal_block(self, node:nodes.literal_block) -> None:
        if node['language'] in self.UNSUPPORTED_LANGUAGES:
            raise nodes.SkipNode
        self._has_code_block = True


    def visit_section(self, node:nodes.section) -> None:
        self._section_level += 1

    def depart_section(self, node:nodes.section) -> None:
        self._section_level -= 1
        self._has_code_block = False

        # Skip section without content
        if not self._secion_has_content(node):
            return
        # Skip toplevel section, we generate :class:`Document` for it
        if self._section_level == 0:
            return

        # TODO: code block
        self.sections.append((Section(node) , node))


    def unknown_visit(self, node:nodes.Node) -> None:
        pass # Ignore any unknown node

    def unknown_departure(self, node:nodes.Node) -> None:
        pass # Ignore any unknown node


    ##################
    # Helper methods #
    ##################

    def _secion_has_content(self, node:nodes.section) -> bool:
        """
        A section has content when it has non-section child node
        (except the title)
        """
        num_subsection = len(list(node[0].traverse(nodes.section,
                                                   descend=False,
                                                   siblings=True)))
        return num_subsection + 1 < len(node)
