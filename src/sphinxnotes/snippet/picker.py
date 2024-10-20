"""
sphinxnotes.snippet.picker
~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippet picker implementations.

:copyright: Copyright 2020 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from docutils import nodes

from sphinx.util import logging

from .snippets import Snippet, Section, Document, Code

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


def pick(
    app: Sphinx, doctree: nodes.document, docname: str
) -> list[tuple[Snippet, nodes.section]]:
    """
    Pick snippets from document, return a list of snippet and the section
    it belongs to.
    """
    # FIXME: Why doctree.source is always None?
    if not doctree.attributes.get('source'):
        logger.debug('Skipped document without source')
        return []

    metadata = app.env.metadata.get(docname, {})
    if 'no-search' in metadata or 'nosearch' in metadata:
        logger.debug('Skipped document with nosearch metadata')
        return []

    # Walk doctree and pick snippets.
    picker = SnippetPicker(doctree)
    doctree.walkabout(picker)

    return picker.snippets


class SnippetPicker(nodes.SparseNodeVisitor):
    """Node visitor for picking snippets from document."""

    #: List of picked snippets and the section it belongs to
    snippets: list[tuple[Snippet, nodes.section]]

    #: Stack of nested sections.
    _sections: list[nodes.section]

    def __init__(self, doctree: nodes.document) -> None:
        super().__init__(doctree)
        self.snippets = []
        self._sections = []

    ###################
    # Visitor methods #
    ###################

    def visit_literal_block(self, node: nodes.literal_block) -> None:
        try:
            code = Code(node)
        except ValueError as e:
            logger.debug(f'skip {node}: {e}')
            raise nodes.SkipNode
        self.snippets.append((code, self._sections[-1]))

    def visit_section(self, node: nodes.section) -> None:
        self._sections.append(node)

    def depart_section(self, node: nodes.section) -> None:
        section = self._sections.pop()
        assert section == node

        # Skip non-leaf section without content
        if self._is_empty_non_leaf_section(node):
            return
        if len(self._sections) == 0:
            self.snippets.append((Document(self.document), node))
        else:
            self.snippets.append((Section(node), node))

    def unknown_visit(self, node: nodes.Node) -> None:
        pass  # Ignore any unknown node

    def unknown_departure(self, node: nodes.Node) -> None:
        pass  # Ignore any unknown node

    ##################
    # Helper methods #
    ##################

    def _is_empty_non_leaf_section(self, node: nodes.section) -> bool:
        """
        A section is a leaf section it has non-child section.
        A section is empty when it has not non-section child node
        (except the title).
        """
        num_subsection = len(
            list(node[0].traverse(nodes.section, descend=False, siblings=True))
        )
        num_nonsection_child = len(node) - num_subsection - 1  # -1 for title
        return num_subsection != 0 and num_nonsection_child == 0
