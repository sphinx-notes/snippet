# Bash Shell key binding for sphinxnotes-picker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-08-14
# :Version: 20240828

function picker_view() {
  selection=$(picker_list)
  [ -z "$selection" ] && return

  # Make sure we have $PAGER
  if [ -z "$PAGER" ]; then
    if  [ ! -z "$(where less)" ]; then
      PAGER='less'
    else
      PAGER='cat'
    fi
  fi

  echo "$PICKER get --src $selection | $PAGER"
}

function picker_edit() {
  selection=$(picker_list --tags ds)
  [ -z "$selection" ] && return

  echo "vim +\$($PICKER get --line-start $selection) \$($PICKER get --file $selection)"
}

function picker_url() {
  selection=$(picker_list --tags ds)
  [ -z "$selection" ] && return

  echo "xdg-open \$($PICKER get --url $selection)"
}

function picker_sh_bind_wrapper() {
  cmd=$($1)
  if [ ! -z "$cmd" ]; then
    eval "$cmd"
  fi
}

function picker_sh_do_bind() {
  bind -x '"\C-kv": picker_sh_bind_wrapper picker_view'
  bind -x '"\C-ke": picker_sh_bind_wrapper picker_edit'
  bind -x '"\C-ku": picker_sh_bind_wrapper picker_url'
}

# Bind key if bind command exists
# (the script may sourced by Zsh)
command -v bind 2>&1 1>/dev/null && picker_sh_do_bind

# vim: set shiftwidth=2:
