"""
    sphinxnotes.snippet
    ~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractclassmethod
import itertools

from docutils import nodes

__title__= 'sphinxnotes-snippet'
__license__ = 'BSD',
__version__ = '1.0b0'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/snippet'
__description__ = 'Non-intrusive literate programming tools for Sphinx documentation'
__keywords__ = 'documentation, sphinx, extension, utility'


class Snippet(ABC):
    """
    Snippet is fragment of reStructuredText documentation.
    It is not always continuous fragment at text (rst) level.

    .. note:: Snippet constructor take doctree nodes as argument,
              please always pass the ``deepcopy()``\ ed nodes to constructor.
    """

    @abstractclassmethod
    def nodes(self) -> List[nodes.Node]:
        """Return the out of tree nodes that make up this snippet."""
        pass


    @abstractclassmethod
    def excerpt(self) -> str:
        """Return excerpt of snippet (for preview)."""
        pass


    @abstractclassmethod
    def kind(self) -> str:
        """Return kind of snippet (for filtering)."""
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
            if not node.line:
                continue # Skip node that have None line, I dont know why :'(
            scopes.append((line_of_start(node), line_of_end(node)))
        scopes = merge_scopes(scopes)
        return scopes


    def original(self) -> List[str]:
        """Return the original reStructuredText text of snippet."""
        # All nodes should have same source file
        srcfn = self.nodes()[0].source
        lines = []
        for scope in self.scopes():
            lines += read_partial_file(srcfn, scope)
        return lines


@dataclass(frozen=True)
class Headline(Snippet):
    """Documentation title and possible subtitle."""
    title:nodes.title
    subtitle:Optional[nodes.title] = None

    def nodes(self) -> List[nodes.Node]:
        if not self.subtitle:
            return [self.title]
        return [self.title, self.subtitle]


    def excerpt(self) -> str:
        if not self.subtitle:
            return '<<%s>>' % self.title.astext()
        return '<<%s ~%s~>>' % (self.title.astext(), self.subtitle.astext())


    def kind(self) -> str:
        return 'd'


@dataclass(frozen=True)
class Notes(Snippet):
    """An abstract :class:`Snippet` subclass."""
    description:List[nodes.Body]

    def nodes(self) -> List[nodes.Node]:
        return self.description.copy()


    def excerpt(self) -> str:
        return self.description[0].astext().replace('\n', '')


@dataclass(frozen=True)
class Code(Notes):
    """A piece of :class:`Notes` with code block."""
    block:nodes.literal_block

    def nodes(self) -> List[nodes.Node]:
        return super().nodes() + [self.block]


    def excerpt(self) -> str:
        return '/*%s*/ ' % self.language() + super().excerpt()


    def kind(self) -> str:
        return 'c'


    def language(self) -> str:
        """Return the (programing) language that appears in code."""
        return self.block['language']


@dataclass(frozen=True)
class Procedure(Notes):
    """
    A piece of :class:`Notes` that describes a sequence of :class:`Code`
    to do something.
    """
    steps:List[Code]

    def nodes(self) -> List[nodes.Node]:
        nodes_ = []
        for code in self.steps:
            nodes_ += code.nodes()
        return super().nodes() + nodes_


    def excerpt(self) -> str:
        return '/*%s*/ ' % ','.join(self.languages()) + super().excerpt()


    def kind(self) -> str:
        return 'p'


    def languages(self) -> Set[str]:
        """Return the (programing) language(s) that appear in procedure."""
        return set(c.block['language'] for c in self.steps)


def read_partial_file(filename:str, scope:Tuple[int,Optional[int]]) -> List[str]:
    lines = []
    with open(filename, "r") as f:
        start = scope[0] - 1
        stop = scope[1] - 1 if scope[1] else None
        for line in itertools.islice(f, start, stop):
            lines.append(line.strip('\n'))
    return lines


def merge_scopes(scopes:List[Tuple[int,Optional[int]]]) -> List[Tuple[int,Optional[int]]]:
    """"Merge the overlap scope, the pass-in scopes must be sorted."""
    # TODO: simplify
    merged = [scopes[0]]
    for tup in scopes[:-1]:
        if merged[-1][1] >= tup[0]:
            if merged[-1][1] >= tup[1]:
                # Completely overlap
                continue
            else:
                # Partial overlap
                merged[-1] = (merged[-1][0], tup[1])
        else:
            # No overlap
            merged.append(tup)
    # Spceial case for last scope
    if merged[-1][1] >= scopes[-1][0]:
        if scopes[-1][1] is None:
            merged[-1] = (merged[-1][0], None)
        elif merged[-1][1] >= scopes[-1][1]:
            # Completely overlap
            pass
        else:
            # Partial overlap
            merged[-1] = (merged[-1][0], scopes[-1][1])
    else:
        # No overlap
        merged.append(tup)

    return merged


def line_of_start(node:nodes.Node) -> int:
    assert node.line
    if isinstance(node, nodes.title):
        if isinstance(node.parent.parent, nodes.document):
            # Spceial case for Document Title / Subtitle
            return 1
        else:
            # Spceial case for section title
            return node.line - 1
    elif isinstance(node, nodes.section):
        if isinstance(node.parent, nodes.document):
            # Spceial case for top level section
            return 1
        else:
            # Spceial case for section
            return node.line - 1
    return node.line


def line_of_end(node:nodes.Node) -> Optional[int]:
    while node:
        next_node = node.next_node(descend=False, siblings=True, ascend=True)
        if next_node and next_node.line:
            return line_of_start(next_node)
        node = next_node
    return None
