# Shell Environment Setup

A Python-based installer for development tools and dotfiles with JSON configuration. This project provides a comprehensive solution for managing your development environment with selective installation, dry-run capabilities, and detailed logging.

## Quick Start

Download and unzip the repository:
```bash
wget https://github.com/arampatzis/shell/archive/refs/heads/master.zip
unzip master.zip
cd shell-master
```
Installation options:
```bash
# Install everything
./install.py

# List available tools
./install.py --list

# Install specific tools
./install.py --components bat fd zellij htop

# Preview changes
./install.py --dry-run

# Force reinstall
./install.py --force
```
## Features


- **Selective Installation**: Install only the tools you need
- **Dry Run Mode**: Preview changes without making them
- **Force Installation**: Override existing installations
- **Comprehensive Logging**: Detailed logs in `install.log`
- **Multiple Sources**: GitHub releases, git clones, source builds
- **Dotfile Management**: Symlink configuration files
- **Error Handling**: Robust error handling with rollback capabilities
- **Type Safety**: Full type hints and modern Python practices

## Requirements

- **Python**: 3.11+
- **Build Tools**: wget, tar, git, make, gcc, autoconf, automake, pkg-config
- **Dependencies**: No dependencies for the installer
