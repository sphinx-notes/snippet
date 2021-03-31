# Z Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :License: BSD

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
  $EDITOR $($snippet get --file $(snippet_list c))
}

# Define a widget, mapped to our function above.
zle -N snippet_view
zle -N snippet_edit

# Bind it to ctrl-kv
bindkey "^kv" snippet_view
# Bind it to ctrl-ke
bindkey "^ke" snippet_edit

# vim: set shiftwidth=2:
