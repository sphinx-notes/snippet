"""
    sphinxnotes.ext.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for sphinxnotes.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Set, TYPE_CHECKING, Dict
import re

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.config import Config as SphinxConfig
from sphinx.util import logging

from .config import Config
from . import Snippet, WithTitle, Document, Section
from .picker import pick
from .cache import Cache, Item
from .keyword import Extractor
from .utils import titlepath
from .builder import Builder


logger = logging.getLogger(__name__)

cache:Cache = None
extractor:Extractor = Extractor()


def extract_tags(s:Snippet) -> str:
    tags = ''
    if isinstance(s, Document):
        tags += 'd'
    elif isinstance(s, Section):
        tags += 's'
    return tags


def extract_excerpt(s:Snippet) -> str:
    if isinstance(s, Document) and s.title is not None:
        return '<' + s.title.text + '>'
    elif isinstance(s, Section) and s.title is not None:
        return '[' + s.title.text + ']'
    return ''


def extract_keywords(s:Snippet) -> List[str]:
    keywords = []
    # TODO: Deal with more snippet
    if isinstance(s, WithTitle) and s.title is not None:
        keywords.extend(extractor.extract(s.title.text, strip_stopwords=False))
    return keywords


def is_document_matched(pats:Dict[str,List[str]], docname:str) -> Dict[str,List[str]]:
    """Whether the docname matched by given patterns pats"""
    new_pats = {}
    for tag, ps in pats.items():
        for pat in ps:
            if re.match(pat, docname):
                new_pats.setdefault(tag, []).append(pat)
    return new_pats


def is_snippet_matched(pats:Dict[str,List[str]], s:[Snippet], docname:str) -> bool:
    """Whether the snippet's tags and docname matched by given patterns pats"""
    if '*' in pats: # Wildcard
        for pat in pats['*']:
            if re.match(pat, docname):
                return True

    not_in_pats = True
    for k in extract_tags(s):
        if k not in pats:
            continue
        not_in_pats = False
        for pat in pats[k]:
            if re.match(pat, docname):
                return True
    return not_in_pats


def on_config_inited(app:Sphinx, appcfg:SphinxConfig) -> None:
    global cache
    cfg = Config(appcfg.snippet_config)
    cache = Cache(cfg.cache_dir)

    try:
        cache.load()
    except Exception as e:
        logger.warning("[snippet] failed to laod cache: %s" % e)


def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                         changed:Set[str], removed:Set[str]) -> List[str]:
    # Remove purged indexes and snippetes from db
    for docname in removed:
        del cache[(app.config.project, docname)]
    return []


def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
    if not isinstance(doctree, nodes.document):
        # XXX: It may caused by ablog
        logger.debug('[snippet] node %s is not nodes.document', type(doctree), location=doctree)
        return

    pats = is_document_matched(app.config.snippet_patterns, docname)
    if len(pats) == 0:
        logger.debug('[snippet] skip picking because %s is not matched', docname)
        return

    doc = []
    snippets = pick(doctree)
    for s, n in snippets:
        if not is_snippet_matched(pats, s, docname):
            continue
        tpath = [x.astext() for x in titlepath.resolve(app.env, docname, n)]
        if isinstance(s, Section):
            tpath = tpath[1:]
        doc.append(Item(snippet=s,
                        tags=extract_tags(s),
                        excerpt=extract_excerpt(s),
                        keywords=extract_keywords(s),
                        titlepath=tpath))

    cache_key = (app.config.project, docname)
    if len(doc) != 0:
        cache[cache_key] = doc
    elif cache_key in cache:
        del cache[cache_key]

    logger.debug('[snippet] picked %s/%s snippetes in %s',
                 len(doc), len(snippets), docname)


def on_builder_finished(app:Sphinx, exception) -> None:
    cache.dump()


def setup(app:Sphinx):
    app.add_builder(Builder)

    app.add_config_value('snippet_config', {}, '')
    app.add_config_value('snippet_patterns', {'*':['.*']}, '')

    app.connect('config-inited', on_config_inited)
    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_builder_finished)
