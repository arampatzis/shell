# Add your own custom alias in the custom/aliases directory. Aliases placed
# here will override ones with the same name in the main alias directory.
#
# Usage:
#
# 1. use the exact naming schema like '<my_aliases>.aliases.sh' where the
#    filename needs to end with .aliases.sh (just <my_aliases>.sh does not
#    work)
# 2. add the leading part of that filename ('<my_aliases>' in this example) to
#    the 'aliases' array in your ~/.bashrc

alias ls='ls  --group-directories-first --color --human-readable'
alias ll='ls -l'

alias grep='grep -n --color=always'

alias bashrc='vim ~/.bashrc;  source ~/.bashrc'
alias vimrc='vim ~/.vimrc'

alias vf='vifm . .'

alias openalias='vim ~/.oh-my-bash/custom/aliases/custom.aliases.sh; source ~/.bashrc'
alias openexports='vim ~/.oh-my-bash/custom/xexports.sh; source ~/.bashrc'
alias opensystem='vim ~/.oh-my-bash/custom/system.sh; source ~/.bashrc'
