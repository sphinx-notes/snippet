# Bash Shell integration for sphinxnotes-snippet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20210814

# Make sure we have $SNIPPET
[ -z "$SNIPPET"] && SNIPPET='snippet'

# Arguments: $1: kinds
# Returns: snippet_id
function snippet_list() {
  $SNIPPET list --tags $1 --width $(($(tput cols) - 2)) | \
    fzf --with-nth 2.. --no-hscroll --header-lines 1    | \
    cut -d ' ' -f1
}

# vim: set shiftwidth=2:
