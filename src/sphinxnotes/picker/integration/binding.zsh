# Z Shell key binding for sphinxnotes-picker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-04-12
# :Version: 20211114

# $1: One of picker_* functions
function picker_z_bind_wrapper() {
  picker_sh_bind_wrapper $1
  zle redisplay
}

function picker_z_view() {
  picker_z_bind_wrapper picker_view
}

function picker_z_edit() {
  picker_z_bind_wrapper picker_edit
}

function picker_z_url() {
  picker_z_bind_wrapper picker_url
}

# Define widgets
zle -N picker_z_view
zle -N picker_z_edit
zle -N picker_z_url

bindkey '^kv' picker_z_view
bindkey '^ke' picker_z_edit
bindkey '^ku' picker_z_url

# vim: set shiftwidth=2:
