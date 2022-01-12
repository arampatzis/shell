#!/bin/bash
# File              : custom.aliases.sh
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 08.03.2021
# Last Modified Date: 08.03.2021
# Last Modified By  : George Arampatzis <garampat@ethz.ch>

alias ls='ls  --group-directories-first --color --human-readable'
alias ll='ls -l'             # Preferred 'ls' implementation

alias grep='grep -n --color=always'

alias bashrc='vim ~/.bashrc;  source ~/.bashrc'
alias vimrc='vim ~/.vimrc'

alias daint='ssh -L 5555:daint.cscs.ch:22 garampat@ela.cscs.ch'
alias ela='ssh -Y ela.cscs.ch'
alias falcon='ssh -Y falcon.ethz.ch'
alias euler='ssh -Y euler.ethz.ch'
alias panda='ssh -Y panda.ethz.ch'
alias barry='ssh -Y barry.ethz.ch'

alias awsfileserver='ssh -Y -i ~/.ssh/id_rsa_aws garampat@aws-fileserver'

alias pythonpath='echo -e ${PYTHONPATH//:/\\n}'
alias librarypath='echo -e ${LIBRARY_PATH//:/\\n}'
alias ldlibrarypath='echo -e ${LD_LIBRARY_PATH//:/\\n}'
alias dyldlibrarypath='echo -e ${DYLD_LIBRARY_PATH//:/\\n}'

alias openalias='vim ~/.oh-my-bash/custom/aliases/custom.aliases.sh; source ~/.bashrc' 
alias openexports='vim ~/.oh-my-bash/custom/xexports.sh; source ~/.bashrc' 
alias opensystem='vim ~/.oh-my-bash/custom/system.sh; source ~/.bashrc' 

alias vf='vifm . .'

alias cp='cp'

if [[ $HOST_NAME == *"epicurus"* ]]; then
  alias cdd='cd $HOME/Desktop/'
  alias cdp='cd $HOME/work/ETH-work/projects'
  alias cdg='cd $HOME/work/ETH-work/projects/2020-graph-sir/python'
  alias cdcode='cd $HOME/work/ETH-work/codes'
  alias cdpiole='cd /Users/garampat/Documents/MATLAB/Sampling/piolet'
  alias updatedb='sudo /usr/libexec/locate.updatedb'
  alias cdk='cd /Users/garampat/work/ETH-work/projects/korali'

  alias ctags="`brew --prefix`/bin/ctags"
  alias cdshell='cd /Users/garampat/work/ETH-work/codes/shell'
fi


if [[ $HOST_NAME == *"euler.ethz.ch"* ]]; then
  alias cds='cd /cluster/scratch/garampat'
  alias bjob='bjobs' #'bjobs -w'
  alias running_users='busers `bugroup | grep "^es_koumo"`'
  alias allocate='bsub -n 4  -Is bash'
  alias quota='/cluster/apps/local/lquota'
fi


if [[ $HOST_NAME == *"barry.ethz.ch"* ]]; then
  alias cds='cd /scratch/garampat'
fi

# aws fileserver
if [[ $HOST_NAME == *"ip-172-16-1-65"* ]]; then
  alias cds='cd /mnt/efs/fs1/'
fi
