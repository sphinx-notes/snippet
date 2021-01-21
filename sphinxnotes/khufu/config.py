"""
    sphinxnotes.khufu.config
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

import os
from os import path
import configparser

from xdg.BaseDirectory import xdg_config_home, xdg_cache_home

ENV = 'KHUFU_CONFIG'

def default() -> configparser.ConfigParser:
    """Return ConfigParser that carries default configuration."""

    config = configparser.ConfigParser()
    config['khufu'] = {}
    config['khufu']['cachedir'] = path.join(xdg_cache_home, 'khufu')
    return config


def load() -> configparser.ConfigParser:
    """Read configuration from file specified by environment variable ``KHUFU_CONFIG``."""
    # Load default config
    config = default()

    # Read from ``$KHUFU_CONFIG`` or ``$XDG_CONFIG_HOME``
    config_fn = os.getenv(ENV) or path.join(xdg_config_home, 'khufu.ini')
    config.read(config_fn)

    cachedir = config['khufu']['cachedir']
    if not path.exists(cachedir):
        os.mkdir(cachedir)

    return config
