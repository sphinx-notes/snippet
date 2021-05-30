# POISX Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20210420

# Make sure we have $SNIPPET
[ -z "$SNIPPET"] && SNIPPET='snippet'

# $1: kinds
function snippet_list() {
  $SNIPPET list --kinds $1 --width $(($(tput cols) - 2))| \
    fzf --with-nth 2.. --no-hscroll --header-lines 1 | \
    cut -d ' ' -f1
}

function snippet_view() {
  index_id=$(snippet_list dc)
  [ -z "$index_id" ] && return

  # Make sure we have $PAGER
  if [ -z "$PAGER" ]; then
    if [ ! -z "$(where bat)" ]; then
      PAGER='bat --language rst --italic-text always --style plain --paging always'
    elif  [ ! -z "$(where less)" ]; then
      PAGER='less'
    elif  [ ! -z "$(where more)" ]; then
      PAGER='more'
    else
      echo "No pager available!" >&2
      return
    fi
  fi

  echo "$SNIPPET get --text $index_id | $PAGER"
}

function snippet_edit() {
  index_id=$(snippet_list dc)
  [ -z "$index_id" ] && return

  # Make sure we have $EDITOR
  if [ -z "$EDITOR" ]; then
    if [ ! -z "$(where vim)" ]; then
      EDITOR='vim'
    elif  [ ! -z "$(where nvim)" ]; then
      EDITOR='nvim'
    elif  [ ! -z "$(where nano)" ]; then
      EDITOR='nano'
    else
      echo "No editor available!" >&2
      return
    fi
  fi

  echo "$EDITOR \$($SNIPPET get --file $index_id)"
}

function snippet_url() {
  index_id=$(snippet_list dc)
  [ -z "$index_id" ] && return

  # Make sure we have $BROWSER
  if [ -z "$BROWSER" ]; then
    if [ ! -z "$(where firefox)" ]; then
      BROWSER='firefox'
    elif  [ ! -z "$(where chromium)" ]; then
      BROWSER='chromium'
    elif  [ ! -z "$(where chrome)" ]; then
      BROWSER='chrome'
    elif  [ ! -z "$(where xdg-open)" ]; then
      BROWSER='xdg-open'
    else
      echo "No browser available!" >&2
      return
    fi
  fi

  echo "$BROWSER \$($SNIPPET get --url $index_id)"
}

# vim: set shiftwidth=2:
