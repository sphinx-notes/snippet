.. This file is generated from sphinx-notes/cookiecutter.
   You need to consider modifying the TEMPLATE or modifying THIS FILE.

===============
sphinxnotes-fzf
===============

.. |docs| image:: https://img.shields.io/github/deployments/sphinx-notes/fzf/github-pages?label=docs
   :target: https://sphinx.silverrainz.me/fzf
   :alt: Documentation Status

.. |license| image:: https://img.shields.io/github/license/sphinx-notes/fzf
   :target: https://github.com/sphinx-notes/fzf/blob/master/LICENSE
   :alt: Open Source License

.. |pypi| image:: https://img.shields.io/pypi/v/sphinxnotes-fzf.svg
   :target: https://pypi.python.org/pypi/sphinxnotes-fzf
   :alt: PyPI Package

.. |download| image:: https://img.shields.io/pypi/dm/sphinxnotes-fzf
   :target: https://pypi.python.org/pypi/sphinxnotes-fzf
   :alt: PyPI Package Downloads

.. |github| image:: https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white/
   :target: https://github.com/sphinx-notes/fzf
   :alt: GitHub Repository

|docs| |license| |pypi| |download| |github|

Introduction
============

.. INTRODUCTION START

Documentations in Sphinx can be parsed into doctree_ (In other words, Abstract Syntax Tree), all contents of documents are parsed into node of this tree. The :ref:`ext` collects snippets (doctree nodes) during the build phase of Sphinx, and provide a :ref:`cli` for your accessing.

For more details, please refer to :doc:`intro`

.. _doctree: https://docutils.sourceforge.io/docs/ref/doctree.html

.. INTRODUCTION END

Getting Started
===============

.. note::

   We assume you already have a Sphinx documentation,
   if not, see `Getting Started with Sphinx`_.

First, downloading extension from PyPI:

.. code-block:: console

   $ pip install sphinxnotes-fzf

Then, add the extension name to ``extensions`` configuration item in your
:parsed_literal:`conf.py_`:

.. code-block:: python

   extensions = [
             # …
             'sphinxnotes.fzf',
             # …
             ]

.. _Getting Started with Sphinx: https://www.sphinx-doc.org/en/master/usage/quickstart.html
.. _conf.py: https://www.sphinx-doc.org/en/master/usage/configuration.html

.. ADDITIONAL CONTENT START

Make sure you have ``snippet`` command in your ``$PATH``.
Rebuild documentation (``make build``), then invoke ``snippet stat``,
the project name is expected to be seen in output.

.. ADDITIONAL CONTENT END

Contents
========

.. toctree::
   :caption: Contents

   intro
   usage
   integration
   changelog

The Sphinx Notes Project
========================

The project is developed by `Shengyu Zhang`__,
as part of **The Sphinx Notes Project**.

.. toctree::
   :caption: The Sphinx Notes Project

   Home <https://sphinx.silverrainz.me/>
   Blog <https://silverrainz.me/blog/category/sphinx.html>
   PyPI <https://pypi.org/search/?q=sphinxnotes>

__ https://github.com/SilverRainZ
