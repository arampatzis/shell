# Bash completion for install.py.
#
# Registered for both "install.py" and "./install.py" so it works regardless
# of whether the script is invoked with an explicit path prefix.
#
# Usage after sourcing ~/.bashrc:
#   ./install.py -<Tab>        show all flags
#   ./install.py -c <Tab>      list available components (fetched live)
#   ./install.py -c dot<Tab>   narrow down to matching components
#
# Component names are fetched by running install.py --list and stripping ANSI
# colour codes, so the list is always in sync with install_config.json.

_install_py_complete() {
    local cur prev opts script components
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="-n --dry-run -f --force -l --list -c --components"

    case "$prev" in
        -c|--components)
            # Resolve install.py relative to the script being completed so this
            # works from any directory, not just the repo root.
            script="$(dirname "$(realpath "${COMP_WORDS[0]}")")/install.py"
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
