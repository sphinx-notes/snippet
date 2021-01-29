"""
    sphinxnotes.khufu.snippet.ext
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension implementation for sphinxnotes.khufu.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import List, Set, Tuple

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from .cache import Cache, Item
from .keyword import Extractor
from .. import config
from ..utils import snippet
from ..utils import titlepath


def setup(app:Sphinx):
    cache = Cache(config.load()['khufu']['cachedir'])

    from .keyword import FrequencyExtractor
    extractor:Extractor = FrequencyExtractor()
    # from .keyword import TextRankExtractor
    # extractor:Extractor = TextRankExtractor()


    def extract_keywords(s:snippet.Code) -> List[Tuple[str,float]]:
        # TODO: Deal with more snippet
        text = '\n'.join([s.title.astext()] + [x.astext() for x in s.content])
        return extractor.extract(text)


    def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                             changed:Set[str], removed:Set[str]) -> List[str]:
        # Remove purged indexes and snippetes from db
        for docname in removed:
            cache.purge(docname)
        return []


    def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
        # FIXME:
        if not isinstance(doctree, nodes.document):
            return

        # Pick code snippet from doctree
        code_picker = snippet.CodePicker(doctree, app.builder)
        doctree.walkabout(code_picker)
        # Resolve title from doctree
        resolver = titlepath.Resolver(doctree, app.builder, docname)
        doctree.walkabout(resolver)

        for code in code_picker.snippets:
            cache.add(Item(project=app.config.project,
                        docname=docname,
                        titlepath=resolver.resolve(code.scopes()[0][0]),
                        snippet=code,
                        keywords=extract_keywords(code)))


    def on_build_finished(app:Sphinx, execption) -> None:
        """ Write literati cache """
        cache.dump()


    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_build_finished)
