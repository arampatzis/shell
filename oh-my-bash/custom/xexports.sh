function path_prepend {
  [[ ":$PATH:" != *":$1:"* ]] && export PATH="$1:${PATH}"
}

echo "Exporting variables..."

export HISTFILESIZE=1000000
export HISTSIZE=1000000

export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
export FZF_DEFAULT_COMMAND="rg --files --hidden -g '!.git/'"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

if [[ "$PATH" == *"pypoetry/virtualenvs"* ]]
then
  # when we create a new shell from inside a poetry shell, we want the new shell to get
  # python from the poetry environment and not from pyenv.
  echo "Inside a Poetry shell. pyenv will not be initialized"
else
  export PYENV_ROOT="$HOME/.pyenv"
  command -v pyenv >/dev/null || path_prepend "$PYENV_ROOT/bin"
  eval "$(pyenv init -)"
fi

if [[ $HOSTNAME == *"epicurus"* ]]; then
  export CC=clang
  export CXX=clang++

  export LIBRARY_PATH="$LIBRARY_PATH:$(brew --prefix llvm)/lib"

  # GNU flavored commands. e.g. ls
  path_prepend "/usr/local/opt/coreutils/libexec/gnubin"
  export MANPATH="/usr/local/opt/coreutils/libexec/gnuman:${MANPATH}"

  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
  export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"

  path_prepend "$HOME/.local/bin"
fi

if [[ $HOSTNAME == *"astakos"* ]]; then

    export PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"

    . "$HOME/.cargo/env"

    path_prepend "$HOME/local/bin"
    path_prepend "$HOME/.local/bin"
fi

echo "Done exporting variables."
