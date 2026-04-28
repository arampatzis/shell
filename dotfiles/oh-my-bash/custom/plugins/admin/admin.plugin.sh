#!/bin/bash
# Admin utilities: SSH user creation and service health checks.

_admin_require_sudo() {
    if ! sudo -v 2>/dev/null; then
        printf "admin: sudo access required\n" >&2
        return 1
    fi
}

_admin_validate_pubkey() {
    local key="$1"
    [[ "$key" =~ ^(ssh-ed25519|ssh-rsa|ssh-ecdsa|ecdsa-sha2-nistp256|sk-ssh-ed25519@openssh.com)[[:space:]] ]]
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
            printf "No key provided. Add it later:\n"
            printf "  echo 'KEY' | sudo tee /home/%s/.ssh/authorized_keys\n" "$username"
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
