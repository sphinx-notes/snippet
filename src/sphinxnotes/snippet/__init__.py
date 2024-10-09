"""
sphinxnotes.snippet
~~~~~~~~~~~~~~~~~~~

:copyright: Copyright 2020 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, TYPE_CHECKING
import itertools
from os import path

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

__version__ = '1.1.1'


class Snippet(object):
    """
    Snippet is base class of reStructuredText snippet.

    :param nodes: Document nodes that make up this snippet
    """

    #: docname where the snippet is located, can be referenced by
    # :rst:role:`doc`.
    docname: str

    #: Absolute path of the source file.
    file: str

    #: Line number range of snippet, in the source file which is left closed
    #: and right opened.
    lineno: Tuple[int, int]

    #: The original reStructuredText of snippet
    rst: List[str]

    #: The possible identifier key of snippet, which is picked from nodes'
    #: (or nodes' parent's) `ids attr`_.
    #:
    #: .. _ids attr: https://docutils.sourceforge.io/docs/ref/doctree.html#ids
    refid: Optional[str]

    def __init__(self, *nodes: nodes.Node) -> None:
        assert len(nodes) != 0

        env: BuildEnvironment = nodes[0].document.settings.env
        self.file = nodes[0].source
        self.docname = env.path2doc(self.file)

        lineno = [float('inf'), -float('inf')]
        for node in nodes:
            if not node.line:
                continue  # Skip node that have None line, I dont know why
            lineno[0] = min(lineno[0], _line_of_start(node))
            lineno[1] = max(lineno[1], _line_of_end(node))
        self.lineno = lineno

        lines = []
        with open(self.file, 'r') as f:
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
    text: str

    def __init__(self, node: nodes.Node) -> None:
        super().__init__(node)
        self.text = node.astext()


class CodeBlock(Text):
    #: Language of code block
    language: str
    #: Caption of code block
    caption: Optional[str]

    def __init__(self, node: nodes.literal_block) -> None:
        assert isinstance(node, nodes.literal_block)
        super().__init__(node)
        self.language = node['language']
        self.caption = node.get('caption')


class WithCodeBlock(object):
    code_blocks: List[CodeBlock]

    def __init__(self, nodes: nodes.Nodes) -> None:
        self.code_blocks = []
        for n in nodes.traverse(nodes.literal_block):
            self.code_blocks.append(self.CodeBlock(n))


class Title(Text):
    def __init__(self, node: nodes.title) -> None:
        assert isinstance(node, nodes.title)
        super().__init__(node)


class WithTitle(object):
    title: Optional[Title]

    def __init__(self, node: nodes.Node) -> None:
        title_node = node.next_node(nodes.title)
        self.title = Title(title_node) if title_node else None


class Section(Snippet, WithTitle):
    def __init__(self, node: nodes.section) -> None:
        assert isinstance(node, nodes.section)
        Snippet.__init__(self, node)
        WithTitle.__init__(self, node)


class Document(Section):
    #: A set of absolute paths of dependent files for document.
    #: Obtained from :attr:`BuildEnvironment.dependencies`.
    deps: set[str]

    def __init__(self, node: nodes.document) -> None:
        assert isinstance(node, nodes.document)
        super().__init__(node.next_node(nodes.section))

        # Record document's dependent files
        self.deps = set()
        env: BuildEnvironment = node.settings.env
        for dep in env.dependencies[self.docname]:
            # Relative to documentation root -> Absolute path of file system.
            self.deps.add(path.join(env.srcdir, dep))


################
# Nodes helper #
################


def _line_of_start(node: nodes.Node) -> int:
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


def _line_of_end(node: nodes.Node) -> Optional[int]:
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
            ascend=True,
            siblings=True,
        )
    # No line found, return the max line of source file
    if node.source:
        with open(node.source) as f:
            return sum(1 for line in f)
    raise AttributeError('None source attr of node %s' % node)
