[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# List all custom OMB plugin functions with their descriptions.
help_plugins() {
    local plugin_dir="$OSH_CUSTOM/plugins"
    [[ -d "$plugin_dir" ]] || { printf "No custom plugins directory found.\n"; return 1; }

    local found=0
    for plugin_file in "$plugin_dir"/*/*.plugin.sh; do
        [[ -f "$plugin_file" ]] || continue
        local plugin_name
        plugin_name=$(basename "$(dirname "$plugin_file")")
        local output
        output=$(awk '
            /^#/ { prev = substr($0, 3); next }
            /^[a-zA-Z_][a-zA-Z0-9_]*\(\)/ {
                name = $1; sub(/\(\).*/, "", name)
                if (substr(name, 1, 1) != "_")
                    printf "  %-22s %s\n", name, prev
            }
            { prev = "" }
        ' "$plugin_file")
        if [[ -n "$output" ]]; then
            printf "\n\033[1;33m%s\033[0m\n" "$plugin_name"
            printf "%s\n" "$output"
            found=1
        fi
    done

    [[ $found -eq 0 ]] && printf "No custom plugins with public functions found.\n"
    return 0
}
