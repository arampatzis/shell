# Contributing

Thank you for your interest in contributing to the Shell Environment Setup project! This document provides guidelines and instructions for contributing effectively.

## Development Setup

### Prerequisites

1. **Python 3.11+**: The project requires Python 3.11 or higher
2. **Poetry**: For dependency management
3. **Git**: For version control
4. **Build Tools**: For testing source installations

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd shell

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Activate the virtual environment
poetry shell

# Verify setup
pre-commit run --all-files
```

## Code Quality Standards

### Pre-commit Hooks

The project uses pre-commit hooks to maintain code quality:

- **Trailing whitespace removal**
- **End-of-file fixer**
- **YAML/TOML validation**
- **Large file detection**
- **Case conflict detection**
- **Executable permissions**
- **Merge conflict detection**
- **Code formatting** (Ruff)
- **Linting** (Ruff)
- **Python version upgrades** (pyupgrade)
- **F-string optimization**

### Code Style Guidelines

- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Add docstrings to all public functions and classes
- **Error Handling**: Implement proper error handling with meaningful messages
- **Logging**: Use the project's logging system for all output
- **Naming**: Follow Python naming conventions (snake_case for functions/variables)


## Adding New Tools

### 1. Binary Tools (GitHub Releases)

For tools distributed as pre-compiled binaries via GitHub releases:

```json
{
  "binary_installer": {
    "new_tool": {
      "binary_name": "new_tool",
      "version": "1.0.0",
      "archive_pattern": "https://github.com/owner/repo/releases/download/v{version}/new_tool-{version}-x86_64-unknown-linux-musl.tar.gz"
    }
  }
}
```

**Requirements**:
- Tool must have GitHub releases
- Archive must contain the binary directly or in a predictable location
- Binary name should match the executable name

### 2. Script Tools (Installation Scripts)

For tools that use installation scripts (curl/wget):

```json
{
  "script_installer": {
    "new_script_tool": {
      "script_url": "https://raw.githubusercontent.com/owner/repo/master/install.sh"
    }
  }
}
```

**Requirements**:
- Script should be idempotent (safe to run multiple times)
- Script should handle its own dependencies
- Consider security implications of running external scripts

### 3. Source Tools (Build from Source)

For tools that need to be compiled from source:

```json
{
  "source_installer": {
    "new_source_tool": {
      "version": "1.0.0",
      "archive_pattern": "https://github.com/owner/repo/archive/refs/tags/{version}.tar.gz",
      "binary_name": "new_source_tool",
      "required_deps": ["gcc", "make", "autoconf", "automake"],
      "run_autogen": true,
      "configure_args": ["--prefix=$HOME/local"],
      "make_args": ["-j4"]
    }
  }
}
```

**Requirements**:
- Source must be available as a tarball
- Build process should be standard (autotools, cmake, etc.)
- Dependencies should be clearly documented

### 4. Dotfiles & Configuration

For configuration files and dotfiles:

```json
{
  "dotfiles_installer": {
    "new_config": {
      "source": "dotfiles/new_config",
      "target": "~/.new_config",
      "expand": true
    }
  }
}
```

**Options**:
- `expand`: Whether to link the source directory to the target directory or link the files in the source directory to the target directory
- `source`: Relative path from project root
- `target`: Destination path (supports `~` expansion)
