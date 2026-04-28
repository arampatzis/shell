#!/bin/bash
# Admin utilities: user management, SSH key auditing, and network visibility.

_admin_require_sudo() {
    if ! sudo -v 2>/dev/null; then
        printf "admin: sudo access required\n" >&2
        return 1
    fi
}

_admin_validate_pubkey() {
    # Accept any key with a valid type prefix followed by base64 data
    [[ "$1" =~ ^[a-zA-Z0-9@._-]+[[:space:]]+[A-Za-z0-9+/]+=*([[:space:]].*)?$ ]]
}

_admin_user_exists() {
    id "$1" &>/dev/null
}

# Create a new user with locked password and SSH key authentication.
# Usage: create_user <username>
create_user() {
    _admin_require_sudo || return 1

    if [[ -z "$1" ]]; then
        printf "Usage: create_user <username>\n"
        return 1
    fi

    local username="$1"

    sudo adduser --disabled-password --gecos "" "$username" || return 1

    local answer
    read -r -p "Add '$username' to the sudo group? [y/N]: " answer
    if [[ "${answer,,}" =~ ^y(es)?$ ]]; then
        sudo usermod -aG sudo "$username"
        printf "Added '%s' to sudo.\n" "$username"
    fi

    sudo mkdir -p "/home/$username/.ssh"

    local pubkey
    while true; do
        printf "Paste the user's public SSH key (or leave blank to skip): "
        read -r pubkey
        if [[ -z "$pubkey" ]]; then
            printf "No key provided. Add it later with: add_pubkey %s\n" "$username"
            break
        elif _admin_validate_pubkey "$pubkey"; then
            printf "%s\n" "$pubkey" | sudo tee "/home/$username/.ssh/authorized_keys" > /dev/null
            break
        else
            printf "Invalid key format. Must start with ssh-ed25519, ssh-rsa, etc.\n"
        fi
    done

    sudo chmod 700 "/home/$username/.ssh"
    sudo chmod 600 "/home/$username/.ssh/authorized_keys" 2>/dev/null
    sudo chown -R "$username:$username" "/home/$username/.ssh"

    local ip
    ip=$(hostname -I | awk '{print $1}')
    printf "\nAccount '%s' created. Login: ssh %s@%s\n" "$username" "$username" "$ip"
}

# Delete a user account and their home directory.
# Usage: delete_user <username>
delete_user() {
    _admin_require_sudo || return 1

    if [[ -z "$1" ]]; then
        printf "Usage: delete_user <username>\n"
        return 1
    fi

    local username="$1"

    if ! _admin_user_exists "$username"; then
        printf "User '%s' does not exist.\n" "$username" >&2
        return 1
    fi

    local answer
    read -r -p "Delete user '$username' and their home directory? [y/N]: " answer
    if [[ ! "${answer,,}" =~ ^y(es)?$ ]]; then
        printf "Aborted.\n"
        return 0
    fi

    sudo deluser --remove-home "$username" && \
        printf "User '%s' and home directory removed.\n" "$username"
}

# Lock a user account (disables login without deleting the account).
# Usage: lock_user <username>
lock_user() {
    _admin_require_sudo || return 1

    if [[ -z "$1" ]]; then
        printf "Usage: lock_user <username>\n"
        return 1
    fi

    if ! _admin_user_exists "$1"; then
        printf "User '%s' does not exist.\n" "$1" >&2
        return 1
    fi

    sudo usermod --lock "$1" && \
        printf "User '%s' locked.\n" "$1"
}

# Unlock a previously locked user account.
# Usage: unlock_user <username>
unlock_user() {
    _admin_require_sudo || return 1

    if [[ -z "$1" ]]; then
        printf "Usage: unlock_user <username>\n"
        return 1
    fi

    if ! _admin_user_exists "$1"; then
        printf "User '%s' does not exist.\n" "$1" >&2
        return 1
    fi

    sudo usermod --unlock "$1" && \
        printf "User '%s' unlocked.\n" "$1"
}

# List all non-system users with their sudo status.
list_users() {
    printf "%-20s %-10s %s\n" "USER" "UID" "SUDO"
    printf "%-20s %-10s %s\n" "----" "---" "----"
    while IFS=: read -r user _ uid _; do
        if (( uid >= 1000 && uid < 65534 )); then
            local sudo_status="no"
            if id -nG "$user" 2>/dev/null | grep -qw "sudo"; then
                sudo_status="yes"
            fi
            printf "%-20s %-10s %s\n" "$user" "$uid" "$sudo_status"
        fi
    done < /etc/passwd
}

# Append an SSH public key to an existing user's authorized_keys.
# Usage: add_pubkey <username>
add_pubkey() {
    _admin_require_sudo || return 1

    if [[ -z "$1" ]]; then
        printf "Usage: add_pubkey <username>\n"
        return 1
    fi

    local username="$1"

    if ! _admin_user_exists "$username"; then
        printf "User '%s' does not exist.\n" "$username" >&2
        return 1
    fi

    local pubkey
    while true; do
        printf "Paste the public SSH key: "
        read -r pubkey
        if _admin_validate_pubkey "$pubkey"; then
            break
        else
            printf "Invalid key format. Must start with ssh-ed25519, ssh-rsa, etc.\n"
        fi
    done

    local home
    home=$(getent passwd "$username" | cut -d: -f6)
    local auth_keys="$home/.ssh/authorized_keys"
    sudo mkdir -p "$home/.ssh"
    printf "%s\n" "$pubkey" | sudo tee -a "$auth_keys" > /dev/null
    sudo chmod 700 "$home/.ssh"
    sudo chmod 600 "$auth_keys"
    sudo chown -R "$username:$username" "$home/.ssh"

    printf "Key added to %s.\n" "$auth_keys"
}

# Show all authorized SSH keys for a user.
# Usage: show_pubkeys <username>
show_pubkeys() {
    if [[ -z "$1" ]]; then
        printf "Usage: show_pubkeys <username>\n"
        return 1
    fi

    if ! _admin_user_exists "$1"; then
        printf "User '%s' does not exist.\n" "$1" >&2
        return 1
    fi

    _admin_require_sudo || return 1

    local home
    home=$(getent passwd "$1" | cut -d: -f6)
    local auth_keys="$home/.ssh/authorized_keys"

    local content
    content=$(sudo cat "$auth_keys" 2>/dev/null)

    if [[ -z "$content" ]]; then
        printf "No keys for '%s'. Add one with: add_pubkey %s\n" "$1" "$1"
        return 0
    fi

    local i=0
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        (( i++ ))
        local keytype comment
        keytype=$(awk '{print $1}' <<< "$line")
        comment=$(awk '{print $3}' <<< "$line")
        printf "[%d] %s  %s\n" "$i" "$keytype" "$comment"
    done <<< "$content"
}

# Show currently logged-in users and their activity.
active_sessions() {
    w -h | awk '{printf "%-12s %-10s %-20s %s\n", $1, $2, $4, $8}'
}

# Show recent login history.
# Usage: last_logins [username]
last_logins() {
    last -n 20 --time-format iso "$@" | grep -v "^$\|wtmp"
}

# Show all listening TCP/UDP ports with the owning process.
open_ports() {
    ss -tlnpu | awk 'NR==1 || /LISTEN/'
}

# Show current firewall rules (requires ufw).
firewall_rules() {
    _admin_require_sudo || return 1
    sudo ufw status numbered
}
