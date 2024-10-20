"""
sphinxnotes.snippet.snippets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitions of various snippets.

:copyright: Copyright 2024 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import itertools
from os import path
import sys

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment


class Snippet(object):
    """
    Snippet is structured fragments extracted from a single Sphinx document
    (usually, also a single reStructuredText file).

    :param nodes: nodes of doctree that make up this snippet.

    .. warning::

       Snippet will be persisted to disk via pickle, to keep it simple,
       it CAN NOT holds reference to any doctree ``nodes``
       (or even any non-std module).
    """

    #: docname where the snippet is located, can be referenced by
    # :rst:role:`doc`.
    docname: str

    #: Absolute path of the source file.
    file: str

    #: Line number range of snippet, in the source file which is left closed
    #: and right opened.
    lineno: tuple[int, int]

    #: The original reStructuredText of snippet
    rst: list[str]

    #: The possible identifier key of snippet, which is picked from nodes'
    #: (or nodes' parent's) `ids attr`_.
    #:
    #: .. _ids attr: https://docutils.sourceforge.io/docs/ref/doctree.html#ids
    refid: str | None

    def __init__(self, *nodes: nodes.Element) -> None:
        assert len(nodes) != 0

        env: BuildEnvironment = nodes[0].document.settings.env

        file, docname = None, None
        for node in nodes:
            if (src := nodes[0].source) and path.exists(src):
                file = src
                docname = env.path2doc(file)
                break
        if not file or not docname:
            raise ValueError('Missing source file or docname')
        self.file = file
        self.docname = docname

        lineno = [sys.maxsize, -sys.maxsize]
        for node in nodes:
            if not node.line:
                continue  # Skip node that have None line, I dont know why
            lineno[0] = min(lineno[0], _line_of_start(node))
            lineno[1] = max(lineno[1], _line_of_end(node))
        self.lineno = (lineno[0], lineno[1])

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


class Code(Snippet):
    #: Language of code block
    lang: str
    #: Description of code block, usually the text of preceding paragraph
    desc: str
    #: The code itself.
    code: str

    def __init__(self, node: nodes.literal_block) -> None:
        assert isinstance(node, nodes.literal_block)
        super().__init__(node)

        self.lang = node['language']
        self.code = node.astext()

        self.desc = ''
        if isinstance(para := node.previous_sibling(), nodes.paragraph):
            # Use the preceding paragraph as descritpion.
            #
            # We usually write some descritpions before a code block, for example,
            # The ``::`` syntax is a common way to create code block::
            #
            #   | Foo::       | <paragraph>
            #   |             |     Foo:
            #   |     Bar     | <literal_block xml:space="preserve">
            #   |             |     Bar
            #
            # In this case, the preceding paragraph "Foo:" is the descritpion
            # of the code block. This convention also applies to the code,
            # code-block, sourcecode directive.
            self.desc += para.astext().replace('\n', ' ')
        if caption := node.get('caption'):
            # Use caption as descritpion.
            # In sphinx, all of code-block, sourcecode and code have caption option.
            # https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
            self.desc += caption
        if not self.desc:
            raise ValueError(
                f'Node f{node} lacks description: a preceding paragraph or a caption'
            )


class WithTitle(object):
    title: str

    def __init__(self, node: nodes.Element) -> None:
        if title := node.next_node(nodes.title):
            self.title = title.astext()
        else:
            raise ValueError(f'Node f{node} lacks title')


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


def _line_of_end(node: nodes.Node) -> int:
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
    if node.source and path.exists(node.source):
        with open(node.source) as f:
            return sum(1 for _ in f)
    raise AttributeError('None source attr of node %s' % node)
