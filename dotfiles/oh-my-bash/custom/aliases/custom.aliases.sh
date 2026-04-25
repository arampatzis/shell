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

alias openalias='vim $OSH_CUSTOM/aliases/custom.aliases.sh; source ~/.bashrc'
alias openexports='vim $OSH_CUSTOM/xexports.sh; source ~/.bashrc'
alias opensystem='vim $OSH_CUSTOM/system.sh; source ~/.bashrc'


if [[ $HOSTNAME == *"tafkoura"* ]]; then
    # General 'ls' replacement with icons and directory grouping
    alias ls='eza --icons --group-directories-first'

    # Detailed list: permissions, human-readable size, and git status
    alias ll='eza -lh --icons --git --group-directories-first'

    # All files (including hidden), with a header row
    alias la='eza -lah --icons --header --group-directories-first'

    # Visual tree view (limited to 3 levels deep)
    alias lt='eza --tree --level=3 --icons'
fi
