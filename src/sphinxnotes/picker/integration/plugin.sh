# Bash Shell integration for sphinxnotes-picker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# :Author: Shengyu Zhang
# :Date: 2021-03-20
# :Version: 20240828

# Make sure we have $PICKER
[ -z "$PICKER"] && PICKER='sphinxnotes-picker'

# Arguments: $*: Extra opts of ``picker list``
# Returns: picker_id
function picker_list() {
  $PICKER list --width $(($(tput cols) - 2)) "$@" | \
    fzf --with-nth 2..      \
        --no-hscroll        \
        --header-lines 1    \
        --margin=2          \
        --border=rounded    \
        --height=60% | cut -d ' ' -f1
}

# vim: set shiftwidth=2:
