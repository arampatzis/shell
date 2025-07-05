#!/usr/bin/env python3
"""
Advanced Dotfiles Installation Script

This script provides a comprehensive solution for managing dotfiles and development 
environment setup. It supports selective installation, dry-run mode, rollback 
capabilities, and detailed logging.
"""
import argparse
import logging
import sys
from pathlib import Path
import yaml

from installers.messages import message as msg
from installers.messages import color
from installers import (
    BinaryInstaller,
    ScriptInstaller,
    SymlinkerInstaller,
    SourceInstaller
)


def load_config():
    """Load configuration from YAML file."""
    config_file = Path("install_config.yaml")
    if not config_file.exists():
        msg.error(f"Configuration file {config_file} not found")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def setup_logging():
    """Configure logging system."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('install.log')
        ]
    )


def install_all_tools(
    dry_run: bool = False,
    components: list[str] | None = None,
    force: bool = False
) -> bool:
    """Install all tools using simple loops."""
    
    # Setup logging
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Get available components
    all_components = []
    all_components.extend(config.get('binary_tools', {}).keys())
    all_components.extend(config.get('script_tools', {}).keys())
    all_components.extend(config.get('source_tools', {}).keys())
    all_components.extend(config.get('dotfile_configs', {}).keys())
    
    # Filter components if specified
    if components:
        invalid_components = set(components) - set(all_components)
        if invalid_components:
            msg.error(f"Invalid components: {', '.join(invalid_components)}")
            msg.custom(f"Available components: {', '.join(all_components)}", color.cyan)
            return False
        target_components = components
    else:
        target_components = all_components
    
    success = True
    
    tools_to_install = {
        "binary_tools": BinaryInstaller,
        "script_tools": ScriptInstaller,
        "source_tools": SourceInstaller,
        "dotfile_configs": SymlinkerInstaller
    }
    
    for tool_type in tools_to_install.keys():
        if config.get(tool_type):
            for tool_name, tool_config in config[tool_type].items():
                if tool_name in target_components:
                    installer = tools_to_install[tool_type](
                        **tool_config,
                        dry_run=dry_run,
                        force=force
                    )
                    if not installer.install():
                        success = False
    # Show results
    if success:
        if dry_run:
            msg.custom("\nDry run completed", color.green)
        else:
            msg.custom("\nInstallation completed successfully", color.green)
    else:
        if dry_run:
            msg.custom(
                "Dry run completed with errors. Check install.log for details.",
                color.yellow
            )
        else:
            msg.custom(
                "Installation completed with errors. "
                "Check install.log for details.", color.yellow
            )
    
    return success


def list_components() -> None:
    """List all available components."""
    config = load_config()
    
    print("Available components:")
    
    if config.get('binary_tools'):
        print("\nBinary tools:")
        for name, tool_config in config['binary_tools'].items():
            print(f"  {name}: {tool_config.get('name', name)}")
    
    if config.get('script_tools'):
        print("\nScript tools:")
        for name, tool_config in config['script_tools'].items():
            print(f"  {name}: {tool_config.get('name', name)}")
    
    if config.get('source_tools'):
        print("\nSource tools:")
        for name, tool_config in config['source_tools'].items():
            print(f"  {name}: {tool_config.get('name', name)}")
    
    if config.get('dotfile_configs'):
        print("\nDotfile configurations:")
        for name, tool_config in config['dotfile_configs'].items():
            print(f"  {name}: {tool_config.get('name', name)}")


def main() -> None:
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Advanced Dotfiles Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Install all components
  %(prog)s --dry-run                # Show what would be installed
  %(prog)s --force                  # Force installation even if already installed
  %(prog)s --components dotfiles config vifm  # Install specific components
  %(prog)s --list-components        # List available components
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be installed without making changes'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force installation even if tools are already installed'
    )
    
    parser.add_argument(
        '--components',
        nargs='+',
        help=(
            "Specific components to install "
            "(use --list-components to see all available)"
        )
    )
    
    parser.add_argument(
        '--list-components',
        action='store_true',
        help='List available components and exit'
    )
    
    args = parser.parse_args()
    
    if args.list_components:
        list_components()
        return
    
    if args.dry_run:
        msg.custom("Dry run mode - No changes will be made", color.green)
    
    success = install_all_tools(
        dry_run=args.dry_run,
        components=args.components,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
