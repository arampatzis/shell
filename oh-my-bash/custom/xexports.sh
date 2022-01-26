
echo "Exporting variables..."

export HISTFILESIZE=1000000
export HISTSIZE=1000000

export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
export FZF_DEFAULT_COMMAND='rg --files'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"


if [[ $HOST_NAME == *"epicurus"* ]]; then
  export CC=clang
  export CXX=clang++

  export PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:${PATH}"
  export PATH="/usr/local/opt/llvm/bin:$PATH"

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


if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  export PATH=$HOME/.local/bin:${PATH}
  export XDG_CACHE_HOME=$HOME/.cache
fi


if [[ $HOST_NAME == *"panda.ethz.ch"* ]]; then
  export PATH="$HOME/.local/bin:${PATH}"
fi

if [[ $HOST_NAME == *"barry.ethz.ch"* ]]; then
  export PATH="$HOME/.local/bin:${PATH}"
  export PATH="$HOME/ai2c/bellport/bin/:${PATH}"

  export PATH=/usr/local/cuda-11.0/bin:${PATH}
  export LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}
  export LD_LIBRARY_PATH=/usr/local/cuda-11.0/lib64:${LD_LIBRARY_PATH}
  export CUDA_HOME=/usr/local/cuda
fi

# aws fileserver
i[[ $HOST_NAME == *"ip-172-31-20-160"* ]]; then
  export PATH="$HOME/.local/bin:${PATH}"
fi

echo "Done exporting variables."
