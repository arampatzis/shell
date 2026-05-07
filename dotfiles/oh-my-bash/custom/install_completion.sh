_install_py_complete() {
    local cur prev opts script
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="-n --dry-run -f --force -l --list -c --components"

    case "$prev" in
        -c|--components)
            script="$(dirname "$(realpath "${COMP_WORDS[0]}")")/install.py"
            local components
            components=$(python3 "$script" --list 2>/dev/null \
                | sed 's/\x1b\[[0-9;]*m//g' \
                | awk '/^  [^ ]/{print $1}')
            COMPREPLY=( $(compgen -W "$components" -- "$cur") )
            return 0
            ;;
    esac

    COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
}

complete -F _install_py_complete install.py
complete -F _install_py_complete ./install.py
