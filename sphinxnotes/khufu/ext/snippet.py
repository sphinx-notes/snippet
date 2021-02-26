"""
    sphinxnotes.khufu.ext.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for sphinxnotes.khufu.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Set, Tuple, TYPE_CHECKING
import re

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from .. import config
from ..snippet import Snippet, Headline, Notes
from ..snippet.picker import pick_doctitle, pick_codes
from ..snippet.cache import Cache, Item
from ..snippet.keyword import Extractor
from ..utils.titlepath import resolve_fullpath, resolve_docpath


logger = logging.getLogger(__name__)

cache:Cache = None

def extract_keywords(s:Snippet) -> List[Tuple[str,float]]:
    from ..snippet.keyword import FrequencyExtractor
    extractor:Extractor = FrequencyExtractor()
    # from ..snippet.keyword import TextRankExtractor
    # extractor:Extractor = TextRankExtractor()

    # TODO: Deal with more snippet
    if isinstance(s, Notes):
        ns = s.description
        return extractor.extract('\n'.join(map(lambda x:x.astext(), ns)))
    elif isinstance(s, Headline):
        ns = []
        if s.title:
            ns.append(s.title)
        if s.subtitle:
            ns.append(s.subtitle)
            # TODO: docname
        return extractor.extract('\n'.join(map(lambda x:x.astext(), ns)))
    else:
        pass


def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                         changed:Set[str], removed:Set[str]) -> List[str]:
    # Remove purged indexes and snippetes from db
    for docname in removed:
        cache.purge_doc(app.config.project, docname)
    return []


def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
    # FIXME:
    if not isinstance(doctree, nodes.document):
        return

    matched = len(app.config.khufu_snippet_patterns) == 0
    for pat in app.config.khufu_snippet_patterns:
        if re.match(pat, docname):
            matched = True
            break

    if not matched:
        cache.purge_doc(app.config.project, docname)
        return

    # Pick document title from doctree
    doctitle = pick_doctitle(doctree)
    cache.add(Item(project=app.config.project,
                   docname=docname,
                   titlepath=resolve_docpath(app.env, docname),
                   snippet=doctitle,
                   keywords=extract_keywords(doctitle)))

    # Pick code snippet from doctree
    codes = pick_codes(doctree)
    for code in codes:
        cache.add(Item(project=app.config.project,
                       docname=docname,
                       titlepath=resolve_fullpath(app.env, doctree, docname, code.nodes()[0]),
                       snippet=code,
                       keywords=extract_keywords(code)))


def on_builder_finished(app:Sphinx, exception) -> None:
    cache.dump()


def setup(app:Sphinx):
    global cache
    cache = Cache(config.load()['khufu']['cachedir'])
    try:
        cache.load()
    except Exception as e:
        logger.warning("failed to laod cache: %s" % e)

    app.add_config_value('khufu_snippet_patterns', [], '')

    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_builder_finished)
