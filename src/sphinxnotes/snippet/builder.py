"""
    sphinxnotes.snippet.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy builder for triggering extension.

    :copyright: Copyright 2021 Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

from sphinx.builders.dummy import DummyBuilder
from sphinx.locale import __


class Builder(DummyBuilder):
    name = 'snippet'
    epilog = __('The snippet builder is a dummy builder for triggering extension.')
