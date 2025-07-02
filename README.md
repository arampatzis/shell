# Advanced Dotfiles Installation Script

A comprehensive, feature-rich dotfiles installation system with object-oriented design, CLI interface, configuration management, and rollback capabilities.

## Features

### ✨ Core Functionality
- **Symlink Management**: Creates symbolic links from your home directory to dotfiles repository
- **Backup System**: Automatically backs up existing files before making changes
- **Component-based Installation**: Install specific components (dotfiles, oh-my-bash, config, etc.)
- **Cross-platform**: Works on macOS, Linux, and other Unix-like systems

### 🚀 Advanced Features
- **CLI Interface**: Rich command-line interface with multiple options
- **Dry Run Mode**: Preview changes without making any modifications
- **Configuration Management**: JSON-based configuration system
- **Rollback Support**: Undo installations with full rollback capability
- **Comprehensive Logging**: Detailed logs with configurable output
- **Dependency Checking**: Validates required tools before installation
- **Test Suite**: Comprehensive unit and integration tests

### 🎯 Supported Components

1. **Dotfiles**: `.bashrc`, `.vimrc`, `.gitconfig`, etc.
2. **Oh My Bash**: Configuration and custom themes/plugins
3. **Config Files**: `.config` directory contents (iTerm2, vifm, etc.)
4. **Vim Snippets**: UltiSnips code snippets
5. **fzf**: Fuzzy finder installation and setup

## Installation

### Prerequisites

- Python 3.6 or higher
- Git
- Bash

### Quick Start

1. Clone your dotfiles repository:
   ```bash
   git clone <your-dotfiles-repo> ~/dotfiles
   cd ~/dotfiles
   ```

2. Run the installer:
   ```bash
   python3 install.py
   ```

## Usage

### Basic Usage

```bash
# Install all components
python3 install.py

# Show what would be installed (dry run)
python3 install.py --dry-run

# Install specific components only
python3 install.py --components dotfiles oh_my_bash

# List available components
python3 install.py --list-components
```

### Advanced Usage

```bash
# Create default configuration file
python3 install.py --create-config

# Use custom configuration file
python3 install.py --config my_config.json

# Rollback last installation
python3 install.py --rollback

# Install with verbose logging
python3 install.py --dry-run  # Check install.log for details
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be installed without making changes |
| `--components <list>` | Install specific components only |
| `--config <file>` | Use custom configuration file |
| `--create-config` | Create default configuration file |
| `--list-components` | List available components |
| `--rollback` | Rollback the last installation |
| `--help` | Show help message |

## Configuration

The installer uses a JSON configuration file (`install_config.json`) to manage settings:

```json
{
  "components": {
    "dotfiles": {
      "enabled": true,
      "source_dir": "dotfiles",
      "description": "Dotfiles (.bashrc, .vimrc, etc.)"
    },
    "oh_my_bash": {
      "enabled": true,
      "source_dir": "oh-my-bash",
      "description": "Oh My Bash configuration"
    },
    "config": {
      "enabled": true,
      "source_dir": "config",
      "description": "Configuration files (.config directory)"
    },
    "vim_snippets": {
      "enabled": true,
      "source_dir": "vim-pluggins",
      "description": "Vim UltiSnips snippets"
    },
    "fzf": {
      "enabled": true,
      "source_dir": "",
      "description": "Fuzzy finder installation"
    }
  },
  "backup": {
    "enabled": true,
    "directory": ".install.bak"
  }
}
```

### Configuration Options

- **enabled**: Whether the component should be installed
- **source_dir**: Directory containing the component files
- **description**: Human-readable description
- **backup.directory**: Where to store backup files

## Directory Structure

```
dotfiles-repo/
├── install.py              # Main installation script
├── install_config.json     # Configuration file
├── messages.py             # Colored output utilities
├── test_installer.py       # Test suite
├── README.md              # This file
├── dotfiles/              # Dotfiles (.bashrc, .vimrc, etc.)
├── oh-my-bash/            # Oh My Bash configuration
│   ├── bashrc
│   └── custom/
├── config/                # .config directory contents
│   ├── iterm2/
│   └── vifm/
└── vim-pluggins/          # Vim plugins and snippets
    └── ultisnips/
```

## Backup and Rollback

### Automatic Backups

The installer automatically creates backups of existing files before making changes:

- Backup location: `.install.bak/` (configurable)
- Backup naming: `filename.YYYY-MM-DD-HHMMSS`
- Operations log: `install_operations.json`

### Rollback Process

```bash
# Rollback the last installation
python3 install.py --rollback
```

The rollback process:
1. Reads the operations log
2. Removes created symlinks
3. Restores backed up files
4. Cleans up the operations log

## Development

### Running Tests

```bash
# Run all tests
python3 test_installer.py

# Run specific test class
python3 -m unittest test_installer.TestInstallConfig

# Run with verbose output
python3 test_installer.py -v
```

### Test Coverage

The test suite includes:
- Configuration management tests
- Rollback functionality tests
- Installer core functionality tests
- CLI interface tests
- Integration tests

### Architecture

The installer follows object-oriented design principles:

```python
# Main classes
DotfilesInstaller    # Core installation logic
InstallConfig        # Configuration management
RollbackManager      # Rollback operations
```

## Examples

### Basic Installation

```bash
# Standard installation of all components
python3 install.py
```

### Selective Installation

```bash
# Install only dotfiles and oh-my-bash
python3 install.py --components dotfiles oh_my_bash

# Install only configuration files
python3 install.py --components config
```

### Preview Changes

```bash
# See what would be installed without making changes
python3 install.py --dry-run
```

### Custom Configuration

```bash
# Create a custom configuration
python3 install.py --create-config
# Edit install_config.json as needed
python3 install.py --config install_config.json
```

### Rollback

```bash
# If something goes wrong, rollback
python3 install.py --rollback
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have write permissions to your home directory
2. **Missing Dependencies**: Install git and bash
3. **Symlink Conflicts**: Existing files are automatically backed up
4. **Oh My Bash Not Found**: Install Oh My Bash first using their installation script

### Debug Information

- Check `install.log` for detailed logging
- Use `--dry-run` to preview changes
- Use `--list-components` to see available components

### Getting Help

```bash
# Show help message
python3 install.py --help

# List available components
python3 install.py --list-components
```

## Comparison with Original

### Before (Original Script)
- ❌ Procedural design
- ❌ No CLI options
- ❌ No configuration management
- ❌ Basic error handling
- ❌ No rollback capability
- ❌ No testing

### After (Enhanced Script)
- ✅ Object-oriented design
- ✅ Rich CLI interface
- ✅ JSON configuration management
- ✅ Comprehensive error handling and logging
- ✅ Full rollback capability
- ✅ Comprehensive test suite
- ✅ Dry-run mode
- ✅ Selective component installation
- ✅ Dependency checking

## License

This project is open source. Feel free to modify and distribute according to your needs.
