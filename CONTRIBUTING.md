# Contributing

Thank you for your interest in contributing to the Shell Environment Setup project! This document provides guidelines and instructions for contributing effectively.

## Development Setup

### Prerequisites

1. **Python 3.11+**: The project requires Python 3.11 or higher
2. **Poetry**: For dependency management
3. **Git**: For version control

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/arampatzis/shell.git ~/projects/shell
cd ~/projects/shell

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Verify setup
pre-commit run --all-files
```

### Running Tests

```bash
python3 -m pytest
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
      "script_url": "https://raw.githubusercontent.com/owner/repo/master/install.sh",
      "check_path": "~/.new_script_tool"
    }
  }
}
```

Use `check_path` or `check_cmd` to prevent re-running on machines where the tool is already installed.

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
      "run_autogen": true
    }
  }
}
```

**Notes**:
- `required_deps`: binaries that must be on `PATH` before building
- `run_autogen`: set to `true` if the source requires running `./autogen.sh` before `./configure`
- The install prefix is set automatically to `~/local`

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
- `expand: true` — each file inside `source/` is symlinked individually into `target/`
- `expand: false` — the `source/` directory itself is symlinked as `target`
- `source`: relative path from project root
- `target`: destination path (supports `~` expansion)
