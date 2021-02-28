"""
    sphinxnotes.ext.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for sphinxnotes.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Set, Tuple, TYPE_CHECKING, Type, Dict
import re

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.config import Config as SphinxConfig
from sphinx.util import logging

from .config import Config
from . import Snippet, Headline, Notes, Code
from .picker import pick_doctitle, pick_codes
from .cache import Cache, Item
from .keyword import Extractor
from .utils.titlepath import resolve_fullpath, resolve_docpath
from .keyword import FrequencyExtractor
# from .keyword import TextRankExtractor


logger = logging.getLogger(__name__)

cache:Cache = None
extractor:Extractor = FrequencyExtractor()
# extractor:Extractor = TextRankExtractor()

def extract_keywords(s:Snippet) -> List[Tuple[str,float]]:
    # TODO: Deal with more snippet
    if isinstance(s, Notes):
        return extractor.extract('\n'.join(map(lambda x:x.astext(), s.description)))
    elif isinstance(s, Headline):
        return extractor.extract('\n'.join(map(lambda x:x.astext(), s.nodes())))
    else:
        logger.warning('unknown snippet instance %s', s)


def is_matched(pats:Dict[str,List[str]], cls:Type[Snippet], docname:str) -> bool:
    # Wildcard
    if '*' in pats:
        for pat in pats['*']:
            if re.match(pat, docname):
                return True
    if cls.kind() in pats:
        for pat in pats[cls.kind()]:
            if re.match(pat, docname):
                return True
    return False


def on_config_inited(app:Sphinx, appcfg:SphinxConfig) -> None:
    global cache
    cfg = Config(appcfg.snippet_config)
    cache = Cache(cfg.cache_dir)

    try:
        cache.load()
    except Exception as e:
        logger.warning("failed to laod cache: %s" % e)


def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                         changed:Set[str], removed:Set[str]) -> List[str]:
    # Remove purged indexes and snippetes from db
    for docname in removed:
        cache.purge_doc(app.config.project, docname)
    return []


def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
    # FIXME:
    if not isinstance(doctree, nodes.document):
        logger.warning('node %s is not nodes.document', type(doctree),
                       location=doctree)
        return

    pats = app.config.snippet_patterns
    matched = False

    # Pick document title from doctree
    if is_matched(pats, Headline, docname):
        matched = True
        doctitle = pick_doctitle(doctree)
        if doctitle:
            cache.add(Item(project=app.config.project,
                           docname=docname,
                           titlepath=resolve_docpath(app.env, docname),
                           snippet=doctitle,
                           keywords=extract_keywords(doctitle)))

    # Pick code snippet from doctree
    if is_matched(pats, Code, docname):
        matched = True
        codes = pick_codes(doctree)
        for code in codes:
            cache.add(Item(project=app.config.project,
                           docname=docname,
                           titlepath=resolve_fullpath(app.env, doctree, docname, code.nodes()[0]),
                           snippet=code,
                           keywords=extract_keywords(code)))

    if not matched:
        cache.purge_doc(app.config.project, docname)


def on_builder_finished(app:Sphinx, exception) -> None:
    cache.dump()


def setup(app:Sphinx):
    app.add_config_value('snippet_config', {}, '')
    app.add_config_value('snippet_patterns', {'*':'.*'}, '')

    app.connect('config-inited', on_config_inited)
    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_builder_finished)
