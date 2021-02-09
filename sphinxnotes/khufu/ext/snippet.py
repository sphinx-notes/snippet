"""
    sphinxnotes.khufu.ext.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for sphinxnotes.khufu.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Set, Tuple, TYPE_CHECKING

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from ..snippet import Code
from ..snippet.picker import CodePicker
from ..snippet.cache import Cache, Item
from ..snippet.keyword import Extractor
from .. import config
from ..utils import titlepath


logger = logging.getLogger(__name__)


def setup(app:Sphinx):
    cache = Cache(config.load()['khufu']['cachedir'])
    try:
        cache.load()
    except Exception as e:
        logger.warning("failed to laod cache: %s" % e)

    from ..snippet.keyword import FrequencyExtractor
    extractor:Extractor = FrequencyExtractor()
    # from ..snippet.keyword import TextRankExtractor
    # extractor:Extractor = TextRankExtractor()


    def extract_keywords(s:Code) -> List[Tuple[str,float]]:
        # TODO: Deal with more snippet
        text = '\n'.join([s.title.astext()] + [x.astext() for x in s.content])
        return extractor.extract(text)


    def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                             changed:Set[str], removed:Set[str]) -> List[str]:
        # Remove purged indexes and snippetes from db
        for docname in removed:
            cache.purge_doc(docname)
        return []


    def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
        # FIXME:
        if not isinstance(doctree, nodes.document):
            return

        # Pick code snippet from doctree
        code_picker = CodePicker(doctree, app.builder)
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
