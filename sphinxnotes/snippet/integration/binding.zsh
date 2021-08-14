# Z Shell key binding for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-04-12
# :Version: 20210814

# $1: One of snippet_* functions
function snippet_z_bind_wrapper() {
  cmd=$($1)
  if [ ! -z "$cmd" ]; then
    BUFFER="$cmd"
    zle accept-line
  fi
}

function snippet_z_edit() {
  snippet_z_bind_wrapper snippet_edit
}

function snippet_z_url() {
  snippet_z_bind_wrapper snippet_url
}

# Define widgets
zle -N snippet_z_edit
zle -N snippet_z_url

bindkey '^ke' snippet_z_edit
bindkey '^ku' snippet_z_url

# vim: set shiftwidth=2:
