============
Introduction
============

Documents in Sphinx can be parsed into doctree_ (In other words, Abstract Syntax Tree), all contents of documents are parsed into node of this tree. The :ref:`ext` collects snippets (doctree nodes) during the build phase of Sphinx, and provide a :ref:`cli` for your accessing.

.. _doctree: https://docutils.sourceforge.io/docs/ref/doctree.html

How It Works
============

In more detail, when collecting snippets, the :ref:`ext` does these things:

- Create unique ID
- Collect meta info of snippet
- Extract keywords from snippet content (In NLP way)

   - For Chinese content, keywords are converted to PinYin

- Dump the aboved information to disk

The :ref:`cli` can read these information from disk, list snippets or get snippet by ID.

What Can This Do
================

It depends on your imagination.

The most common usage is, feed snippet list to a fuzzy finder like Fzf_, we can search the snippet by fuzzy keywords. Once we get the snippet ID, we can access all its meta information, view its source code, edit its corresponding file, open its corresponding HTML documentation...

Which means, you can integrate your most handy tools with Sphinx by writing scripts. We also provide some examples about this, please refer to :doc:`integration`.

.. _Fzf: https://github.com/junegunn/fzf
