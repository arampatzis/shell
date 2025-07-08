#!/bin/bash

echo "Setting up ssh-agent..."

# Find an existing ssh-agent socket for this user
SOCK=$(find /tmp -type s -name "agent.*" -user "$USER" 2>/dev/null | head -n 1)

if [ -z "$SOCK" ]; then
    echo "No running ssh-agent found. Starting a new agent..."
    eval "$(ssh-agent -s)"
else
    export SSH_AUTH_SOCK="$SOCK"
    echo "Connected to ssh-agent at $SSH_AUTH_SOCK"
fi

# Check and add keys if they exist
for key in ~/.ssh/id_ed25519 ~/.ssh/github; do
    if [ -f "$key" ]; then
        echo "Adding key: $key"
        ssh-add "$key"
    else
        echo "Key not found: $key"
    fi
done
