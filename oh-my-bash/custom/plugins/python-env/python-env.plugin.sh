#!/bin/bash
# File              : python-env.plugin.sh
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 20.01.2022 18:00
# Last Modified Date: 20.01.2022 18:32
# Last Modified By  : George Arampatzis <garampat@ethz.ch>

if [ -d ~/.venv ]; then
  export VENV_ROOT=~/.venv
else
  mkdir ~/.venv
fi

venv-new() {
  python3 -m venv $VENV_ROOT/$1
}

venv-activate() {
  source $VENV_ROOT/$1/bin/activate
}
