# Shell Environment Setup

A Python-based installer for development tools and dotfiles with JSON configuration. This project provides a comprehensive solution for managing your development environment with selective installation, dry-run capabilities, and detailed logging.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/arampatzis/shell.git ~/projects/shell && cd ~/projects/shell
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
- **Multiple Sources**: GitHub releases, script installers, source builds
- **Dotfile Management**: Symlink configuration files with automatic backup
- **Type Safety**: Full type hints and modern Python practices

## Migration Guide

### OMB custom directory (one-time, existing machines only)

Previous versions symlinked your custom files into `~/.oh-my-bash/custom`, which is inside OMB's own git repo. This dirtied that repo and blocked OMB from auto-updating. The fix moves your custom files to `~/.omb-custom` (outside OMB's repo) and sets `OSH_CUSTOM` accordingly.

Run this once on any machine that has the old setup:

```bash
rm ~/.oh-my-bash/custom
git -C ~/.oh-my-bash checkout -- custom/
./install.py --components omb_config
```

Verify it worked:

```bash
ls ~/.omb-custom/                          # your custom aliases, plugins, exports
git -C ~/.oh-my-bash status               # clean — no deleted files
source ~/.oh-my-bash/tools/upgrade.sh    # OMB update succeeds
```

New machines are unaffected — the installer creates `~/.omb-custom` directly.

## Requirements

- **Python**: 3.11+
- **Build Tools**: wget, tar, git, make, gcc, autoconf, automake, pkg-config
- **Dependencies**: No dependencies for the installer
