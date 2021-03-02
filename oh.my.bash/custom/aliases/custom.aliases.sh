# Add your own custom alias in the custom/aliases directory. Aliases placed
# here will override ones with the same name in the main alias directory.

alias ls='ls  --group-directories-first --color --human-readable'
alias ll='ls -l'             # Preferred 'ls' implementation

alias grep='grep -n --color=always'

alias bashrc='vim ~/.bashrc;  source ~/.bashrc'
alias vimrc='vim ~/.vimrc'

alias cdd='cd $HOME/Desktop/'
alias cdp='cd $HOME/work/ETH-work/projects'
alias cdg='cd $HOME/work/ETH-work/projects/2020-graph-sir/python'
alias cdc='cd $HOME/work/projects/covid19'
alias cdpiole='cd /Users/garampat/Documents/MATLAB/Sampling/piolet'

alias updatedb='sudo /usr/libexec/locate.updatedb'

alias updateallpython='python3 -m pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | cut -d : -f 2 | xargs -n1 pip install -U'

alias matlab='/Applications/MATLAB_R2019a.app/bin/matlab &'

export KORALI=$HOME/work/ETH-work/projects/korali/
alias cdk='cd $KORALI'
alias cda='cd $KORALI_APPS'

alias daint='ssh -L 5555:daint.cscs.ch:22 garampat@ela.cscs.ch'
alias ela='ssh -Y ela.cscs.ch'

alias falcon='ssh -Y falcon.ethz.ch'
alias euler='ssh -Y euler.ethz.ch'
alias panda='ssh -Y panda.ethz.ch'
alias barry='ssh -Y barry.ethz.ch'

alias pythonpath='echo -e ${PYTHONPATH//:/\\n}'
