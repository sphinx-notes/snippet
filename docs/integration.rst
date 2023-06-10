===========
Integration
===========

Currently we provide integration for Bash, Zsh, and Vim, you can use the following fucntion after you activated the corresponding configuration (see subsections).
Beside, Fzf_ is always required.

.. _Fzf: https://github.com/junegunn/fzf

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
