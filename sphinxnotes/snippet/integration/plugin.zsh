# Z Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20210420
#
# NOTE: Must source :file:`./plugin.sh` to get snippet_* functions.

# $1: One of snippet_* functions
function z-wrapper() {
  cmd=$($1)
  if [ ! -z "$cmd" ]; then
    BUFFER="$cmd"
    zle accept-line
  fi
}

function snippet-view(){ z-wrapper snippet_view }
function snippet-edit(){ z-wrapper snippet_edit }
function snippet-url(){ z-wrapper snippet_url }

# Define a widget
zle -N snippet-view
zle -N snippet-edit
zle -N snippet-url

# vim: set shiftwidth=2:
