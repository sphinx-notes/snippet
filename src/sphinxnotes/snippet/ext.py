"""
sphinxnotes.snippet.ext
~~~~~~~~~~~~~~~~~~~~~~~

Sphinx extension implementation, but the entrypoint is located at __init__.py.

:copyright: Copyright 2024 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import re
from os import path
import time

from docutils import nodes
from sphinx.locale import __
from sphinx.util import logging
from sphinx.builders.dummy import DummyBuilder

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.config import Config as SphinxConfig
    from collections.abc import Iterator

from .config import Config
from .snippets import Snippet, WithTitle, Document, Section, Code
from .picker import pick
from .cache import Cache, Item
from .keyword import Extractor
from .utils import titlepath


logger = logging.getLogger(__name__)

cache: Cache | None = None
extractor: Extractor = Extractor()


def extract_tags(s: Snippet) -> str:
    tags = ''
    if isinstance(s, Document):
        tags += 'd'
    elif isinstance(s, Section):
        tags += 's'
    elif isinstance(s, Code):
        tags += 'c'
    return tags


def extract_excerpt(s: Snippet) -> str:
    if isinstance(s, Document) and s.title is not None:
        return '<' + s.title + '>'
    elif isinstance(s, Section) and s.title is not None:
        return '[' + s.title + ']'
    elif isinstance(s, Code):
        return '`' + (s.lang + ':').ljust(8, ' ') + ' ' + s.desc + '`'
    return ''


def extract_keywords(s: Snippet) -> list[str]:
    keywords = [s.docname]
    if isinstance(s, WithTitle) and s.title is not None:
        keywords.extend(extractor.extract(s.title, strip_stopwords=False))
    if isinstance(s, Code):
        keywords.extend(extractor.extract(s.desc, strip_stopwords=False))
    return keywords


def _get_document_allowed_tags(pats: dict[str, list[str]], docname: str) -> str:
    """Return the tags of snippets that are allowed to be picked from the document."""
    allowed_tags = ''
    for tags, ps in pats.items():
        for pat in ps:
            if re.match(pat, docname):
                allowed_tags += tags
    return allowed_tags


def on_config_inited(app: Sphinx, appcfg: SphinxConfig) -> None:
    global cache
    cfg = Config(appcfg.snippet_config)
    cache = Cache(cfg.cache_dir)

    try:
        cache.load()
    except Exception as e:
        logger.warning('[snippet] failed to laod cache: %s' % e)


def on_env_get_outdated(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    # Remove purged indexes and snippetes from db
    assert cache is not None
    for docname in removed:
        del cache[(app.config.project, docname)]
    return []


def on_doctree_resolved(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    if not isinstance(doctree, nodes.document):
        # XXX: It may caused by ablog
        logger.debug(
            '[snippet] node %s is not nodes.document', type(doctree), location=doctree
        )
        return

    allowed_tags = _get_document_allowed_tags(app.config.snippet_patterns, docname)
    if not allowed_tags:
        logger.debug('[snippet] skip picking: no tag allowed for document %s', docname)
        return

    doc = []
    snippets = pick(app, doctree, docname)
    for s, n in snippets:
        # FIXME: Better filter logic.
        if extract_tags(s) not in allowed_tags:
            continue
        tpath = [x.astext() for x in titlepath.resolve(app.env, docname, n)]
        if isinstance(s, Section):
            tpath = tpath[1:]
        doc.append(
            Item(
                snippet=s,
                tags=extract_tags(s),
                excerpt=extract_excerpt(s),
                keywords=extract_keywords(s),
                titlepath=tpath,
            )
        )

    cache_key = (app.config.project, docname)
    assert cache is not None
    if len(doc) != 0:
        cache[cache_key] = doc
    elif cache_key in cache:
        del cache[cache_key]

    logger.debug(
        '[snippet] picked %s/%s snippetes in %s', len(doc), len(snippets), docname
    )


def on_builder_finished(app: Sphinx, exception) -> None:
    assert cache is not None
    cache.dump()


class SnippetBuilder(DummyBuilder):  # DummyBuilder has dummy impls we need.
    name = 'snippet'
    epilog = __(
        'The snippet builder produces snippets (not to OUTPUTDIR) for use by snippet CLI tool'
    )

    def get_outdated_docs(self) -> Iterator[str]:
        """Modified from :py:meth:`sphinx.builders.html.StandaloneHTMLBuilder.get_outdated_docs`."""
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                logger.debug('[build target] did not in env: %r', docname)
                yield docname
                continue

            assert cache is not None
            targetname = cache.itemfile((self.app.config.project, docname))
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    logger.debug(
                        '[build target] targetname %r(%s), docname %r(%s)',
                        targetname,
                        _format_modified_time(targetmtime),
                        docname,
                        _format_modified_time(
                            path.getmtime(self.env.doc2path(docname))
                        ),
                    )
                    yield docname
            except OSError:
                # source doesn't exist anymore
                pass


def _format_modified_time(timestamp: float) -> str:
    """Return an RFC 3339 formatted string representing the given timestamp."""
    seconds, fraction = divmod(timestamp, 1)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(seconds)) + f'.{fraction:.3f}'
