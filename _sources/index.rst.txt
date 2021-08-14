===================
sphinxnotes-snippet
===================

.. image:: https://img.shields.io/github/stars/sphinx-notes/snippet.svg?style=social&label=Star&maxAge=2592000
   :target: https://github.com/sphinx-notes/snippet

:version: |version|
:copyright: Copyright ©2021 by Shengyu Zhang.
:license: BSD, see LICENSE for details.

Inspecting snippets of Sphinx documentation.

.. _Sphinx: https://www.sphinx-doc.org/

.. contents:: Table of Contents
   :local:
   :backlinks: none

Introduction
============

Documents in Sphinx can be parsed into doctree_ (In other words, Abstract Syntax Tree), all contents of documents are parsed into node of this tree. The :ref:`ext` collects snippets (meaningful doctree_ nodes) during the build phase of Sphinx, and provide a :ref:`cli` for your accessing.

.. _doctree: https://docutils.sourceforge.io/docs/ref/doctree.html

How It Works
------------

In more detail, when collecting snippets, the :ref:`ext` does these things:

- Create unique ID
- Collect meta info of snippet
- Extract keywords from snippet content (In NLP way)

   - For Chinese content, keywords are converted to PinYin

- Dump the aboved information to disk

The :ref:`cli` can read these information from disk, list snippets or get snippet by ID.

What Can This Do
----------------

It depends on your imagination.

The most common usage is, feed snippet list to a fuzzy finder like Fzf_, we can search the snippet by fuzzy keywords. Once we get the snippet ID, we can access all its meta information, view its source code, edit its corresponding file, open its corresponding HTML documentation...

Which means, you can integrate your most handy tools with Sphinx by writing scripts. We also provide some examples about this, please refer to :ref:`integration`.

.. _Fzf: https://github.com/junegunn/fzf

Installation
============

1. Download it from official Python Package Index:

   .. code-block:: console

      # pip install sphinxnotes-snippet

2. Make sure you have ``snippet`` command in your ``$PATH``
3. Add extension to :file:`conf.py` in your Sphinx project:

   .. code-block:: python

       extensions = [
                 # …
                 'sphinxnotes.snippet.ext',
                 # …
                 ]

4. Rebuild documentation, then invoke ``snippet stat``, the project name is expected to be seen in output.

.. _integration:

Integration
===========

Currently we provide integration for Bash, Zsh, and Vim, you can use the following fucntion after you activated the corresponding configuration (see subsections).
Beside, Fzf_ is always required.

Fast Edit
   :Shortcut: :kbd:`Ctrl+k,e`

   Fuzzy find snippet with Fzf_ and edit corresponding file with vim

   .. note:: :kbd:`Ctrl+k,e` means: Press :kbd:`Ctrl+k` first, then press :kbd:`e` immediately, same below

Fast View HTML
   :Shortcut: :kbd:`Ctrl+k,u`

   Fuzzy find snippet with Fzf_ and open its corresponding HTML URL with xdg-open

   .. note:: Before use this function, you should configurate ``base_url`` in CLI tool :ref:`cli-conf`

Bash
----

Add the following code to your :file:`~/.bashrc`:

.. code-block:: bash

   eval "$(snippet integration --sh --sh-binding)"

Zsh
---

Add the following code to your :file:`~/.zshrc`:

.. code-block:: zsh

   eval "$(snippet integration --zsh --zsh-binding)"

Fast edit demo:

.. asciinema:: /_assets/zsh.cast

Vim
---

Add the following code to your :file:`~/.vimrc`:

.. code-block:: vim

   let snippet_vim = tempname()
   call system('snippet integration --vim --vim-binding>' . snippet_vim)
   execute 'source ' . snippet_vim
   call delete(snippet_vim)

Fast edit demo:

.. asciinema:: /_assets/vim.cast

Usage
=====

.. _ext:

Extension
---------

Append ``sphinxnotes.snippet.ext`` to Sphinx extensions.

Configuration
~~~~~~~~~~~~~

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
-----------------

See ``snippet --help`` for usage.

.. _cli-conf:

Configuration
~~~~~~~~~~~~~

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


Change Log
==========

2021-08-14 1.0b7
----------------

.. sectionauthor:: Shengyu Zhang

- snippet: Add support for section
- integration: Drop snippet view support
- Complete document

2021-03-20 1.0b2
----------------

.. sectionauthor:: Shengyu Zhang

- Improve keywords extraction
- Speed up snippet dumping
- Code clean up

2021-02-28 1.0b1
----------------

.. sectionauthor:: Shengyu Zhang

- Refactor!!!
- Rename from sphinxnotes-khufu

2021-02-01 1.0a1
----------------

.. sectionauthor:: Shengyu Zhang

- Dont evaluate typing annoations on runtime
- Speed up snippet cache
- Speed up title path resolving
- Better tokenizer
- A lot of bug fixes
- Add config khufu_snippet_patterns

2021-01-29 1.0a0
----------------

.. sectionauthor:: Shengyu Zhang

The alpha version is out, enjoy~
