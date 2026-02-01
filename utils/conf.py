# Snippet confiuration for test purpose.

from os import path

cache_dir = '/tmp/sphinxnotes-picker'

base_urls = {
    'sphinxnotes-picker': 'file://'
    + path.join(path.dirname(path.dirname(path.realpath(__file__))), 'doc/_build/html'),
}
