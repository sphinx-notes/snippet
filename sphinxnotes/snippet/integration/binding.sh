# Bash Shell key binding for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-08-14
# :Version: 20211114

function snippet_view() {
  selection=$(snippet_list ds)
  [ -z "$selection" ] && return

  # Make sure we have $PAGER
  if [ -z "$PAGER" ]; then
    if  [ ! -z "$(where less)" ]; then
      PAGER='less'
    else
      PAGER='cat'
    fi
  fi

  echo "$SNIPPET get --text $selection | $PAGER"
}

function snippet_edit() {
  selection=$(snippet_list ds)
  [ -z "$selection" ] && return

  echo "vim +\$($SNIPPET get --line-start $selection) \$($SNIPPET get --file $selection)"
}

function snippet_url() {
  selection=$(snippet_list ds)
  [ -z "$selection" ] && return

  echo "xdg-open \$($SNIPPET get --url $selection)"
}

function snippet_sh_bind_wrapper() {
  cmd=$($1)
  if [ ! -z "$cmd" ]; then
    eval "$cmd"
  fi
}

function snippet_sh_do_bind() {
  bind -x '"\C-kv": snippet_sh_bind_wrapper snippet_view'
  bind -x '"\C-ke": snippet_sh_bind_wrapper snippet_edit'
  bind -x '"\C-ku": snippet_sh_bind_wrapper snippet_url'
}

# Bind key if bind command exists
# (the script may sourced by Zsh)
command -v bind 2>&1 1>/dev/null && snippet_sh_do_bind

# vim: set shiftwidth=2:
