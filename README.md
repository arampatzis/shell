# Dotfiles Installation Script

Advanced dotfiles installer with symlink management, backup system, and rollback capabilities.

## Features

- **Symlink Management**: Links dotfiles to home directory
- **Automatic Backups**: Backs up existing files to `.install.bak/`
- **Component Installation**: Install specific parts (dotfiles, oh-my-bash, config, fzf)
- **Dry Run Mode**: Preview changes without applying them
- **Rollback Support**: Undo installations completely

## Quick Start

```bash
# Install everything
./install.py

# Preview what would be installed
./install.py --dry-run

# Install specific components
./install.py --components dotfiles oh_my_bash_configuration

# List available components
./install.py --list-components

# Rollback last installation
./install.py --rollback
```

## Components

- **oh_my_bash_installation**: Checks if oh-my-bash is installed
- **dotfiles**: Links `.bashrc`, `.vimrc`, `.gitconfig`, etc.
- **oh_my_bash_configuration**: Links oh-my-bash config and custom directory
- **config**: Links configuration files to `~/config/`
- **fzf**: Installs fuzzy finder

## Directory Structure

```
shell/
├── install.py
├── data/
│   ├── dotfiles/          # Home directory dotfiles
│   ├── oh-my-bash/        # Oh-my-bash configuration
│   │   ├── .bashrc
│   │   └── custom/
│   └── config/            # Application configs
│       ├── iterm2/
│       └── vifm/
└── .install.bak/          # Automatic backups
```

## Notes

- Backups are created automatically in `.install.bak/`
- Existing symlinks to same source are skipped
- Operations are logged for rollback capability
- Requires oh-my-bash to be pre-installed
