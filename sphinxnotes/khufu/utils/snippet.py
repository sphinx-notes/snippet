"""
    sphinxnotes.utils.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
from abc import ABC, abstractclassmethod
import itertools

from docutils import nodes

from sphinx.builders import Builder
from sphinx.util.docutils import SphinxTranslator


def next_nonchild_node(node:nodes.Node) -> nodes.Node:
    """Helper function for returing next sibling or ascend node."""
    return node.next_node(descend=False, siblings=True, ascend=True)


def next_sibling_node(node:nodes.Node) -> nodes.Node:
    """Helper function for returing next sibling node."""
    return node.next_node(descend=False, siblings=True, ascend=False)


def read_partial_file(filename:str, scope:Tuple[int,Optional[int]]) -> List[str]:
    lines = []
    with open(filename, "r") as f:
        # Index = Lineno - 1
        start = scope[0] - 1
        stop = scope[1] - 1 if scope[1] else None
        for line in itertools.islice(f, start, stop):
            lines.append(line.strip('\n'))
    return lines


def merge_scopes(scopes:List[Tuple[int,Optional[int]]]) -> List[Tuple[int,Optional[int]]]:
    """"Merge the overlap scope, the pass-in scopes must be sorted."""
    merged = [scopes[0]]
    for tup in scopes[1:]:
        if merged[-1][1] is None or merged[-1][1] >= tup[0]:
            if merged[-1][1] is None or (tup[1] is not None and merged[-1][1] >= tup[1]):
                # Completely overlap
                continue
            else:
                # Partial overlap
                merged[-1] = (merged[-1][0], tup[1])
        else:
            # No overlap
            merged.append(tup)
    return merged


class Snippet(ABC):
    """
    Snippet is a meaningful fragment of reStructuredText documentations.
    It is not always continuous fragment at text (rst) level.
    """

    @abstractclassmethod
    def nodes(self) -> List[nodes.Node]:
        """
        Return the doctree nodes that make up the snippet.
        """
        pass


    def scopes(self) -> List[Tuple[int,Optional[int]]]:
        """
        Return the scopes of snippet, which corresponding to the line
        number in the source file.

        A scope is a left closed and right open interval of the line number
        ``[left, right)``. Snippet is not continuous in source file so we return
        a list of scope.
        """
        scopes = []
        for node in self.nodes():
            after_node = next_nonchild_node(node)
            if after_node and after_node.line:
                # TODO: document why node.line - 1
                # after_node.line - 1 for right open
                scopes.append((node.line - 1, after_node.line - 1))
            else:
                # EOF
                scopes.append((node.line - 1, None))
        return merge_scopes(scopes)


    def rst(self) -> List[str]:
        """
        Return the reStructuredText representation of snippet.

        .. note:: The returned text may not consecutive paragraphs in original
                  documentations.
        """
        # All nodes should have same source file
        srcfn = self.nodes()[0].source
        lines = []
        for scope in self.scopes():
            lines += read_partial_file(srcfn, scope)
        return lines


@dataclass(frozen=True)
class Notes(Snippet):
    # nodes.term is term if definition_list_item::
    #
    #     <definition_list_item>
    #         <term>
    #             foo
    #         <definition>
    #             <paragraph>
    #                 bar
    title:Union[nodes.title,nodes.term]
    content:List[nodes.Body]


    def nodes(self) -> List[nodes.Node]:
        return [self.title] + self.content


    def excerpt(self) -> str:
        """Return excerpt of snippet (for preview)."""
        if not self.content:
            # FIXME: 
            return '<no content>'
        excerpt = self.content[0].astext().replace('\n', '')
        return excerpt[:30] # TODO: Magic number for now


@dataclass(frozen=True)
class Code(Notes):
    code:nodes.literal_block

    def nodes(self) -> List[nodes.Node]:
        return super().nodes() + [self.code]


    def excerpt(self) -> str:
        return '[%s] ' % self.language() + super().excerpt()


    def language(self) -> str:
        """ Return the (programing) language of the code. """
        return self.code.attributes['language']


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
