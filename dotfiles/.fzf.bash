# Setup fzf
# ---------
if [[ ! "$PATH" == */home/garampat/.fzf/bin* ]]; then
  export PATH="${PATH:+${PATH}:}/home/garampat/.fzf/bin"
fi

# Auto-completion
# ---------------
[[ $- == *i* ]] && source "/home/garampat/.fzf/shell/completion.bash" 2> /dev/null

# Key bindings
# ------------
source "/home/garampat/.fzf/shell/key-bindings.bash"
