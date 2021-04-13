# Z Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20210412

snippet="snippet"

# $1: kinds
function snippet_list() {
  $snippet list --kinds $1 --width $(($(tput cols) - 2))| \
    fzf --with-nth 2.. --no-hscroll --header-lines 1 | \
    cut -d ' ' -f1
}

function snippet_view() {
  $snippet get --text $(snippet_list c)
}

function snippet_edit() {
  BUFFER="$EDITOR $($snippet get --file $(snippet_list dc))"
  zle accept-line
}

function snippet_url() {
  BUFFER="$BROWSER $($snippet get --url $(snippet_list dc))"
  zle accept-line
}

# Define a widget, mapped to our function above.
zle -N snippet-view snippet_view
zle -N snippet-edit snippet_edit
zle -N snippet-url snippet_url

# vim: set shiftwidth=2:
