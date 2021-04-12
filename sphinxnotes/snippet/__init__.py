"""
    sphinxnotes.snippet
    ~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass, field
from abc import ABC, abstractclassmethod
import itertools

from docutils import nodes


__title__= 'sphinxnotes-snippet'
__license__ = 'BSD',
__version__ = '1.0b3'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/snippet'
__description__ = 'Non-intrusive snippet manager for Sphinx documentation'
__keywords__ = 'documentation, sphinx, extension, utility'

NODE_METADATA = 'node'

@dataclass
class Snippet(ABC):
    """
    Snippet is a {abstract,data}class represents a snippet of reStructuredText
    documentation. Note that it is not always continuous fragment at text (rst)
    level.
    """
    _scopes:List[Tuple[int,int]] = field(init=False)
    _refid:Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post-init processing routine of dataclass"""

        # Calcuate scope before deepcopy
        scopes = []
        for node in self.nodes():
            if not node.line:
                continue # Skip node that have None line, I dont know why :'(
            scopes.append((line_of_start(node), line_of_end(node)))
        self._scopes = merge_scopes(scopes)

        # Find exactly one id attr in nodes
        self._refid = None
        for node in self.nodes():
            if node['ids']:
                self._refid = node['ids'][0]
                break
        # If no node has id, use parent's
        if not self._refid:
            for node in self.nodes():
                if node.parent['ids']:
                    self._refid = node.parent['ids'][0]
                    break

        # Separate all nodes from doctree
        for f in self.__class__.__dataclass_fields__.values():
            if not f.metadata.get(NODE_METADATA, False):
                continue
            v = getattr(self, f.name)
            if v is None:
                continue
            elif isinstance(v, nodes.Node):
                setattr(self, f.name, v.deepcopy())
            elif isinstance(v, list):
                setattr(self, f.name, [n.deepcopy() for n in v])
            else:
                raise NotImplementedError(type(v))


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


    def file(self) -> str:
        """Return source file path of snippet"""
        # All nodes should have same source file
        return self.nodes()[0].source


    def scopes(self) -> List[Tuple[int,int]]:
        """
        Return the scopes of snippet, which corresponding to the line
        number in the source file.

        A scope is a left closed and right open interval of the line number
        ``[left, right)``. Snippet is not continuous in source file so we return
        a list of scope.
        """
        return self._scopes


    def text(self) -> List[str]:
        """Return the original reStructuredText text of snippet."""
        srcfn = self.file()
        lines = []
        for scope in self.scopes():
            lines += read_partial_file(srcfn, scope)
        return lines


    def refid(self) -> Optional[str]:
        """
        Return the possible identifier key of snippet.
        It is picked from nodes' (or nodes' parent's) `ids attr`_.

        .. _ids attr: https://docutils.sourceforge.io/docs/ref/doctree.html#ids
        """
        return self._refid


@dataclass
class Headline(Snippet):
    """Documentation title and possible subtitle."""
    title:nodes.title = field(metadata={NODE_METADATA:True})
    subtitle:Optional[nodes.title] = field(metadata={NODE_METADATA:True})

    def nodes(self) -> List[nodes.Node]:
        if not self.subtitle:
            return [self.title]
        return [self.title, self.subtitle]


    def excerpt(self) -> str:
        if not self.subtitle:
            return '<%s>' % self.title.astext()
        return '<%s ~%s~>' % (self.title.astext(), self.subtitle.astext())


    @classmethod
    def kind(cls) -> str:
        return 'd'


@dataclass
class Notes(Snippet):
    """An abstract :class:`Snippet` subclass."""
    description:List[nodes.Body] = field(metadata={NODE_METADATA:True})

    def nodes(self) -> List[nodes.Node]:
        return self.description.copy()


    def excerpt(self) -> str:
        return self.description[0].astext().replace('\n', '')


@dataclass
class Code(Notes):
    """A piece of :class:`Notes` with code block."""
    block:nodes.literal_block = field(metadata={NODE_METADATA:True})

    def nodes(self) -> List[nodes.Node]:
        return super().nodes() + [self.block]


    def excerpt(self) -> str:
        return '/%s/ ' % self.language() + super().excerpt()


    @classmethod
    def kind(cls) -> str:
        return 'c'


    def language(self) -> str:
        """Return the (programing) language that appears in code."""
        return self.block['language']


@dataclass
class Procedure(Notes):
    """
    A piece of :class:`Notes` that describes a sequence of :class:`Code`
    to do something.

    FIXME: how to use NODE_METADATA
    """
    steps:List[Code]

    def nodes(self) -> List[nodes.Node]:
        nodes_ = []
        for code in self.steps:
            nodes_ += code.nodes()
        return super().nodes() + nodes_


    def excerpt(self) -> str:
        return '/%s/ ' % ','.join(self.languages()) + super().excerpt()


    @classmethod
    def kind(cls) -> str:
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


def merge_scopes(scopes:List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    """"Merge the overlap scope, the pass-in scopes must be sorted."""
    merged = [scopes[0]]
    for tup in scopes:
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
    next_node = node.next_node(descend=False, siblings=True, ascend=True)
    while next_node:
        if next_node.line:
            return line_of_start(next_node)
        next_node = next_node.next_node(
            # Some nodes' line attr is always None, but their children has
            # valid line attr
            descend=True,
            # If node and its children have not valid line attr, try use line
            # of next node
            ascend=True, siblings=True)
    # No line found, return the max line of source file
    if node.source:
        with open(node.source) as f:
            return sum(1 for line in f)
    raise AttributeError('None source attr of node %s' % node)
