# @Author: Georgios Arampatzis <garampat>
# @Date:   2021-02-28T22:02:28+01:00
# @Email:  garampat@ethz.ch
# @Last modified by:   garampat
# @Last modified time: 2021-02-28T22:07:08+01:00


# export BASH_SILENCE_DEPRECATION_WARNING=1

export HISTFILESIZE=1000000
export HISTSIZE=1000000

export PIOLE=$HOME/Documents/MATLAB/Sampling/piolet

export CXX=g++-10
export CC=gcc-10

export PATH="/usr/local/opt/llvm/bin:$PATH"

export LIBRARY_PATH="$LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"
export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:/usr/local/Cellar/gsl/2.6/lib/"

#----------------------------------------------------------------------------------
# GNU flavored commands. e.g. ls
export PATH="/usr/local/opt/coreutils/libexec/gnubin:${PATH}"
export MANPATH="/usr/local/opt/coreutils/libexec/gnuman:${MANPATH}"
#----------------------------------------------------------------------------------

# Setting PATH for Python 3.9
export PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:${PATH}"

export LIBRARY_PATH="$LIBRARY_PATH:`brew --prefix llvm`/lib"

export FZF_DEFAULT_COMMAND='find .'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"


HOST=`hostname -d`
if [[ $HOST == "euler.ethz.ch" ]]; then

  export PATH=$PATH:$HOME/bin
  export PATH=$HOME/usr/bin:$PATH
  export PATH=$HOME/usr/ctags/bin:$PATH
  export PATH=$HOME/usr/valgrind/bin:$PATH
  export PATH=$HOME/.local/bin:$PATH

  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/usr/lib
  export XDG_CACHE_HOME=$HOME/.cache

fi

