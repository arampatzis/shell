
if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  # Setup fzf
  # ---------
  if [[ ! "$PATH" == */cluster/home/garampat/.fzf/bin* ]]; then
    export PATH="${PATH:+${PATH}:}/cluster/home/garampat/.fzf/bin"
  fi

  # Auto-completion
  # ---------------
  [[ $- == *i* ]] && source "/cluster/home/garampat/.fzf/shell/completion.bash" 2> /dev/null

  # Key bindings
  # ------------
  source "/cluster/home/garampat/.fzf/shell/key-bindings.bash"
fi
