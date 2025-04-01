function path_prepend {
    [[ ":$PATH:" != *":$1:"* ]] && export PATH="$1:${PATH}"
}

echo "Exporting variables..."

export HISTFILESIZE=1000000
export HISTSIZE=1000000

export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
export FZF_DEFAULT_COMMAND="rg --files --hidden -g '!.git/'"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

export SCIAGRAPH_ACCESS_KEY=e7f320b8-ea81-4ee8-897c-801cf1d2530e
export SCIAGRAPH_ACCESS_SECRET=jc_ttcoDfpy7cmEV1ZWCyQYFcnEG38IW87WiDPi6nEAbAuRWRIgawtogY1IO26dRPUZ-kNm3kt3XbeyITsJXBA==

if [[ "$PATH" == *"pypoetry/virtualenvs"* ]]
then
  # when we create a new shell from inside a poetry shell, we want the new shell to get
  # python from the poetry environment and not from pyenv.
  echo "Inside a Poetry shell. pyenv will not be initialized"
else
  export PYENV_ROOT="$HOME/.pyenv"
  command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"
fi

if [[ $HOST_NAME == *"epicurus"* ]]; then
  export CC=clang
  export CXX=clang++

  export PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:${PATH}"
  export PATH="/usr/local/opt/llvm/bin:$PATH"
  export PATH="/Users/garampat/Library/Python/3.9/bin:$PATH"

  export LIBRARY_PATH="$LIBRARY_PATH:`brew --prefix llvm`/lib"

  # GNU flavored commands. e.g. ls
  export PATH="/usr/local/opt/coreutils/libexec/gnubin:${PATH}"
  export MANPATH="/usr/local/opt/coreutils/libexec/gnuman:${MANPATH}"

  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
  export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"

  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi

if [[ $HOSTNAME == *"astakos"* ]]; then

    path_prepend "$HOME/local/bin"

    export PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"

    . "$HOME/.cargo/env"

    export PATH="$PATH:/home/thodoros/storage/arampatzis/.local/bin"
fi

echo "Done exporting variables."
