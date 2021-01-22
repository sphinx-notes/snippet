"""
    sphinxnotes.utils.titlepath
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import List, Dict,Optional, Tuple

from docutils import nodes

from sphinx.builders import Builder
from sphinx.util.docutils import SphinxTranslator

UNTITLED = 'Untitled'
SEP = '/'

class Resolver(SphinxTranslator):

    _docname:str
    # Sorted list of (line number, structural node)
    _sections:List[Tuple[int,nodes.Structural]]
    # Title of structural nodes
    _section_titles:Dict[nodes.Structural,str]
    # Title path of document
    _document_path:List[str]


    def __init__(self, document:nodes.document, builder: Builder, docname:str) -> None:
        super().__init__(document, builder)

        self._docname = docname
        self._sections = []
        self._section_titles = {}
        # Document path is set at first resolve
        self._document_path = None


    def visit_document(self, node:nodes.document) -> None:
        self._sections.append((0, node))


    def visit_Structural(self, node:nodes.Structural) -> None:
        self._sections.append((node.line, node))
        self._sections.sort(key=lambda tup: tup[0])


    def visit_title(self, node:nodes.title) -> None:
        self._section_titles[node.parent] = node.astext()


    def unknown_visit(self, node:nodes.Node) -> None:
        # Ignore any unknown node
        pass


    def unknown_departure(self, node:nodes.Node) -> None:
        # Ignore any unknown node
        pass


    def resolve(self, lineno:int,
                include_document_path:bool=True,
                include_document_title:bool=True) -> List[str]:
        if not self._document_path:
            self._document_path = self._resolve_document_path(self._docname)

        node = None
        for i, tup in enumerate(self._sections):
            if lineno < tup[0]:
                if i > 1:
                    # Get previous node if have
                    node = self._sections[i-1][1]
                else:
                    # Else use root node
                    node = self._sections[0][1]
                break
        if not node:
            # Use last node if not node matched
            node = self._sections[-1][1]

        loc = self._document_path.copy()
        while node:
            title = self._section_titles.get(node)
            if title:
                loc = [title] + loc 
            else:
                loc = [UNTITLED] + loc 
            node = node.parent

        return loc


    def _resolve_document_title(self, docname:str) -> Optional[str]:
        if not self.builder.env:
            return None
        if not docname in self.builder.env.found_docs:
            raise KeyError('Document %s not found in build environment' % docname)
        elif not docname in self.builder.env.titles:
            return None
        else:
            return self.builder.env.titles[docname].astext()


    def _resolve_document_path(self, docname:str) -> List[str]:
        loc = []

        # Get titles of all master docs appear on the path of given docname
        # TODO: any toctree
        slices = docname.split(SEP)
        master_doc = self.config.master_doc
        for i, s in enumerate(slices):
            master_docname = SEP.join(slices[0:i] + [master_doc])
            loc.append(self._resolve_document_title(master_docname) or UNTITLED)
        # Get title of given docname
        if slices[-1] != master_doc:
            loc.append(self._resolve_document_title(docname) or UNTITLED)

        return loc

