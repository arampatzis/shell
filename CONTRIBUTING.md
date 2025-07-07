# Contributing

Thanks for your interest! Here are the main ways to contribute:

## Adding New Tools

1. **Binary Tools** (GitHub releases):
   ```yaml
   tool_name:
     name: "Tool Name"
     binary_name: "tool"
     repo: "owner/repo"
     version: "v1.0.0"
     archive_pattern: "https://github.com/{repo}/releases/download/{version}/tool-{version}-x86_64-unknown-linux-musl.tar.gz"
     check_cmd: "tool"
   ```

2. **Source Tools** (build from source):
   ```yaml
   tool_name:
     name: "Tool Name"
     repo: "owner/repo"
     version: "v1.0.0"
     archive_pattern: "https://github.com/{repo}/archive/refs/tags/{version}.tar.gz"
     binary_name: "tool"
     build_deps: ["wget", "tar", "make", "gcc"]
     configure_args: ["--prefix=$HOME/local"]
     run_autogen: true  # if needed
     check_cmd: "tool"
   ```

## Improving Installers

- **Binary**: Enhance `installers/binary.py` for different archive formats
- **Script**: Improve `installers/script.py` for new script patterns
- **Source**: Extend `installers/source.py` for complex build systems
- **Symlinker**: Add features to `installers/symlinker.py` for advanced linking

## Testing

```bash
# Test specific tool
./install.py --components tool_name --dry-run

# Test installation
./install.py --components tool_name --force
```

## Code Style

- Use type hints
- Follow existing patterns
- Add error handling
- Update documentation

## Code Guidelines

- Keep functions focused and testable
- Use type hints and docstrings
- Follow existing naming conventions
- Test changes with `--dry-run` first

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a PR with clear description

## Issues

Report bugs or request features via GitHub Issues. Include:
- OS and Python version
- Error logs from `install.log`
- Steps to reproduce
