
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

alias pythonpath='echo -e ${PYTHONPATH//:/\\n}'


if [[ $HOST_NAME == "epicurus" ]]; then
  alias cdd='cd $HOME/Desktop/'
  alias cdp='cd $HOME/work/ETH-work/projects'
  alias cdg='cd $HOME/work/ETH-work/projects/2020-graph-sir/python'
  alias cdcode='cd $HOME/work/ETH-work/codes'
  alias cdpiole='cd /Users/garampat/Documents/MATLAB/Sampling/piolet'
  alias updatedb='sudo /usr/libexec/locate.updatedb'
  KORALI=$HOME/work/ETH-work/projects/korali/
  alias cdk='cd $KORALI'
  alias cda='cd $KORALI_APPS'
fi


if [[ $HOST_NAME == "euler.ethz.ch" ]]; then
  alias cds='cd /cluster/scratch/garampat'
  alias bjob='bjobs' #'bjobs -w'
  alias running_users='busers `bugroup | grep "^es_koumo"`'
  alias allocate='bsub -n 4  -Is bash'
  alias quota='/cluster/apps/local/lquota'
fi
