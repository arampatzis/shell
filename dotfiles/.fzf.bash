
# Set the fzf installation folder
if [[ $HOST_NAME == *"epicurus"* ]]; then
  fzf_path="/usr/local/opt/fzf/"
elif [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  fzf_path="/cluster/home/garampat/.fzf/"
fi

# Setup fzf
if [[ ! "$PATH" == *$fzf_path/bin* ]]; then
  export PATH="${PATH:+${PATH}:}$fzf_path/bin"
fi

[[ $- == *i* ]] && source "$fzf_path/shell/completion.bash" 2> /dev/null

source "$fzf_path/shell/key-bindings.bash"
