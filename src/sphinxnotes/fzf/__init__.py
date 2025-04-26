"""
sphinxnotes.snippet
~~~~~~~~~~~~~~~~~~~

Sphinx extension entrypoint.

:copyright: Copyright 2024 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""


def setup(app):
    # **WARNING**: We don't import these packages globally, because the current
    # package (sphinxnotes.snippet) is always resloved when importing
    # sphinxnotes.snippet.*. If we import packages here, eventually we will
    # load a lot of packages from the Sphinx. It will seriously **SLOW DOWN**
    # the startup time of our CLI tool (sphinxnotes.snippet.cli).
    #
    # .. seealso:: https://github.com/sphinx-notes/snippet/pull/31
    from .ext import (
        SnippetBuilder,
        on_config_inited,
        on_env_get_outdated,
        on_doctree_resolved,
        on_builder_finished,
    )

    app.add_builder(SnippetBuilder)

    app.add_config_value('snippet_config', {}, '')
    app.add_config_value('snippet_patterns', {'*': ['.*']}, '')

    app.connect('config-inited', on_config_inited)
    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_builder_finished)
