=====
Usage
=====

.. _ext:

Extension
=========

Append ``sphinxnotes.snippet.ext`` to Sphinx extensions.

Configuration
-------------

The extension provides the following configuration:

:snippet_config:
   :Type: ``Dict[str,Any]``

   Custom CLI tool :ref:`cli-conf`.

   .. attention:: Maybe deprecated in future

:snippet_patterns:
   :Type: ``Dict[str,List[str]]``
   :Default: ``{'*': ['.*']}``)

   A "snippet tags" →  "regular expression list" mapping.

   If a snippet's tags are not included in the dict, or the snippet's docname_ does not matched by the any of regular expression of corresponding list, it wil be filtered.

   The default vaule ``{'*': ['.*']}`` matchs any snippet.

   .. note:: See `snippet --help` for available snippet tags

.. _docname: https://www.sphinx-doc.org/en/master/glossary.html#term-document-name

.. _cli:

Command Line Tool
=================

See ``snippet --help`` for usage.

.. _cli-conf:

Configuration
-------------

The configuration of CLI tools is a python script, located at :file:`$XDG_CONFIG_HOME/sphinxnotes/snippet/conf.py`, Usually :file:`~/.config/sphinxnotes/snippet/conf.py`.

:cache_dir:
   :Type: ``str``
   :Default: ``"$XDG_CACHE_HOME/sphinxnotes/snippet"``

   Path to snippet cache directory.

:base_url:
   :Type: ``Dict[str,str]``
   :Default: ``{}``

   A "project name" →  "base URL" mapping. It is used as prefix of snippet URL when you invoke ``snippet get --url <SNIPPET_ID>``

   Base URL can point to your Sphinx site or local HTML file. For local file, URL should use "file://" schema (required by ``xdg-open``), such as: "file:///home/la/documents/bullet/_build/html/".

   .. note:: Project name is the `project confval`_ of your Sphinx project.

      .. _project confval: https://www.sphinx-doc.org/en/master/usage/configuration.html?highlight=project#confval-project
