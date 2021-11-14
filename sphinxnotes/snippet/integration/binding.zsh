# Z Shell key binding for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-04-12
# :Version: 20211114

# $1: One of snippet_* functions
function snippet_z_bind_wrapper() {
  snippet_sh_bind_wrapper $1
  zle redisplay
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
