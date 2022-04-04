"""
    sphinxnotes.snippet
    ~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
import itertools

from docutils import nodes


__title__= 'sphinxnotes-snippet'
__license__ = 'BSD'
__version__ = '1.1.1'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/snippet'
__description__ = 'Non-intrusive snippet manager for Sphinx documentation'
__keywords__ = 'documentation, sphinx, extension, utility'

class Snippet(object):
    """
    Snippet is base class of reStructuredText snippet.

    :param nodes: Document nodes that make up this snippet 
    """

    #: Source file path of snippet
    file:str

    #: Line number range of snippet, in the source file which is left closed
    #: and right opened.
    lineno:Tuple[int,int]

    #: The original reStructuredText of snippet
    rst:List[str]

    #: The possible identifier key of snippet, which is picked from nodes'
    #: (or nodes' parent's) `ids attr`_.
    #:
    #: .. _ids attr: https://docutils.sourceforge.io/docs/ref/doctree.html#ids
    refid:Optional[str]

    def __init__(self, *nodes:nodes.Node) -> None:
        assert len(nodes) != 0

        self.file = nodes[0].source

        lineno = [float('inf'), -float('inf')]
        for node in nodes:
            if not node.line:
                continue # Skip node that have None line, I dont know why
            lineno[0] = min(lineno[0], _line_of_start(node))
            lineno[1] = max(lineno[1], _line_of_end(node))
        self.lineno = lineno

        lines = []
        with open(self.file, "r") as f:
            start = self.lineno[0] - 1
            stop = self.lineno[1] - 1
            for line in itertools.islice(f, start, stop):
                lines.append(line.strip('\n'))
        self.rst = lines

        # Find exactly one ID attr in nodes
        self.refid = None
        for node in nodes:
            if node['ids']:
                self.refid = node['ids'][0]
                break

        # If no ID found, try parent
        if not self.refid:
            for node in nodes:
                if node.parent['ids']:
                    self.refid = node.parent['ids'][0]
                    break



class Text(Snippet):
    #: Text of snippet
    text:str

    def __init__(self, node:nodes.Node) -> None:
        super().__init__(node)
        self.text = node.astext()


class CodeBlock(Text):
    #: Language of code block
    language:str
    #: Caption of code block
    caption:Optional[str]

    def __init__(self, node:nodes.literal_block) -> None:
        assert isinstance(node, nodes.literal_block)
        super().__init__(node)
        self.language = node['language']
        self.caption = node.get('caption')


class WithCodeBlock(object):
    code_blocks:List[CodeBlock]

    def __init__(self, nodes:nodes.Nodes) -> None:
        self.code_blocks = []
        for n in nodes.traverse(nodes.literal_block):
            self.code_blocks.append(self.CodeBlock(n))


class Title(Text):
    def __init__(self, node:nodes.title) -> None:
        assert isinstance(node, nodes.title)
        super().__init__(node)


class WithTitle(object):
    title:Optional[Title]

    def __init__(self, node:nodes.Node) -> None:
        title_node = node.next_node(nodes.title)
        self.title = Title(title_node) if title_node else None


class Section(Snippet, WithTitle):
    def __init__(self, node:nodes.section) -> None:
        assert isinstance(node, nodes.section)
        Snippet.__init__(self, node)
        WithTitle.__init__(self, node)


class Document(Section):
    def __init__(self, node:nodes.document) -> None:
        assert isinstance(node, nodes.document)
        super().__init__(node.next_node(nodes.section))


################
# Nodes helper #
################

def _line_of_start(node:nodes.Node) -> int:
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


def _line_of_end(node:nodes.Node) -> Optional[int]:
    next_node = node.next_node(descend=False, siblings=True, ascend=True)
    while next_node:
        if next_node.line:
            return _line_of_start(next_node)
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
