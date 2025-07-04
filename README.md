# Shell Environment Setup

A Python-based installer for development tools and dotfiles with YAML configuration.

## Quick Start

```bash
# Install everything
./install.py

# Install specific tools
./install.py --components bat fd zellij htop

# Preview changes
./install.py --dry-run

# List available tools
./install.py --list-components

# Force reinstall
./install.py --force
```

## Available Tools

**Binary Tools**: lazygit, ripgrep, bat, fd, zellij, gh  
**Script Tools**: fzf, oh-my-bash  
**Source Tools**: vifm, htop  
**Dotfiles**: bash, vim, git configs, oh-my-bash themes

## Features

- **Selective Installation**: Install only the tools you need
- **Dry Run Mode**: Preview changes without making them
- **Force Installation**: Override existing installations
- **Comprehensive Logging**: Detailed logs in `install.log`
- **Multiple Sources**: GitHub releases, git clones, source builds
- **Dotfile Management**: Symlink configuration files

## Configuration

Edit `install_config.yaml` to customize:
- Tool versions and sources
- Build dependencies
- Installation paths
- Dotfile locations

## Requirements

- Python 3.8+
- Basic build tools (wget, tar, git, make, gcc)

## Project Structure

```
shell/
├── install.py              # Main installer script
├── install_config.yaml     # Tool configurations  
├── installers/             # Installer classes (binary, script, source, symlink)
├── dotfiles/               # Dotfiles and configs
└── messages.py             # UI messaging utilities
```
