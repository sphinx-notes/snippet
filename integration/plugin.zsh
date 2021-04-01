# Z Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :License: BSD
#
# The recommanded key bindings are::
#
#   bindkey ^kv snippet-view
#   bindkey ^ke snippet-edit

snippet="snippet"

# $1: kinds
function snippet_list() {
  $snippet list --kinds $1 | \
    fzf --with-nth 2.. --no-hscroll --header-lines 1 | \
    cut -d ' ' -f1
}

function snippet_view() {
  $snippet get --text $(snippet_list c)
}

function snippet_edit() {
  $EDITOR $($snippet get --file $(snippet_list dc))
}

# Define a widget, mapped to our function above.
zle -N snippet-view snippet_view
zle -N snippet-edit snippet_edit

# vim: set shiftwidth=2:
