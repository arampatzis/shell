
export HISTFILESIZE=1000000
export HISTSIZE=1000000

export FZF_DEFAULT_COMMAND='find .'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"


if [[ $HOST_NAME == *"epicurus"* ]]; then
  export CXX=g++-10
  export CC=gcc-10

  export PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:${PATH}"
  export PATH="/usr/local/opt/llvm/bin:$PATH"

  export LIBRARY_PATH="$LIBRARY_PATH:`brew --prefix llvm`/lib"
  
  # GNU flavored commands. e.g. ls
  export PATH="/usr/local/opt/coreutils/libexec/gnubin:${PATH}"
  export MANPATH="/usr/local/opt/coreutils/libexec/gnuman:${MANPATH}"

  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
  export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
fi


if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  export PATH=$PATH:$HOME/bin
  export PATH=$HOME/usr/bin:$PATH
  export PATH=$HOME/usr/ctags/bin:$PATH
  export PATH=$HOME/usr/valgrind/bin:$PATH
  export PATH=$HOME/.local/bin:$PATH

  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/usr/lib
  export XDG_CACHE_HOME=$HOME/.cache
fi


if [[ $HOST_NAME == *"panda.ethz.ch"* ]]; then
  export PATH="$HOME/.local/bin:${PATH}"
fi
