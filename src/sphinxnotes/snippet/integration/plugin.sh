# Bash Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20240828

# Make sure we have $SNIPPET
[ -z "$SNIPPET"] && SNIPPET='snippet'

# Arguments: $*: Extra opts of ``snippet list``
# Returns: snippet_id
function snippet_list() {
  $SNIPPET list --width $(($(tput cols) - 2)) "$@" | \
    fzf --with-nth 2..      \
        --no-hscroll        \
        --header-lines 1    \
        --margin=2          \
        --border=rounded    \
        --height=60% | cut -d ' ' -f1
}

# vim: set shiftwidth=2:
