#!/bin/bash

# Find an existing ssh-agent socket for this user
SOCK=$(find /tmp -type s -name "agent.*" -user "$USER" 2>/dev/null | head -n 1)

if [ -z "$SOCK" ]; then
    eval "$(ssh-agent -s)" >/dev/null
else
    export SSH_AUTH_SOCK="$SOCK"
fi

# Add keys if they exist
for key in ~/.ssh/id_ed25519 ~/.ssh/github; do
    [ -f "$key" ] && ssh-add "$key" 2>/dev/null
done
