# Shell Environment Setup

A Python-based installer for dotfiles and development tools with YAML configuration.

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
```

## Available Tools

**Binary Tools**: lazygit, ripgrep, bat, fd, zellij  
**Script Tools**: fzf, oh-my-bash  
**Source Tools**: vifm, htop  
**Dotfiles**: bash, vim, git configs

## Configuration

Edit `install_config.yaml` to add tools or modify versions. Supports:
- GitHub binary releases
- Git clone + scripts  
- Source builds with autogen
- Dotfile symlinking

## Requirements

- Python 3.8+
- Basic build tools (wget, tar, git, make, gcc)

## Structure

```
shell/
├── install.py              # Main installer
├── install_config.yaml     # Tool configurations  
├── installers/             # Installer classes
└── data/                   # Dotfiles and configs
```
