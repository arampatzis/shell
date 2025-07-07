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
import json
from pathlib import Path
import traceback

from installers.messages import message as msg
from installers.messages import color
from installers import (
    BinaryInstaller,
    ScriptInstaller,
    SymlinkerInstaller,
    SourceInstaller
)


INSTALLERS_MAP = {
    "binary_installer": BinaryInstaller,
    "script_installer": ScriptInstaller,
    "source_installer": SourceInstaller,
    "dotfiles_installer": SymlinkerInstaller
}


def load_config():
    """Load configuration from JSON file."""
    config_file = Path("install_config.json")
    if not config_file.exists():
        msg.error(f"Configuration file {config_file} not found")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        return json.load(f)


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
    tools_to_install: list[str] | None = None,
    force: bool = False
) -> bool:
    """Install all tools using simple loops."""
    
    log_file = "install.log"
    
    setup_logging()
    
    config = load_config()
    
    available_tools = []
    for tool in INSTALLERS_MAP.keys():
        available_tools.extend(config.get(tool, {}).keys())
        
    if tools_to_install:
        invalid_components = set(tools_to_install) - set(available_tools)
        if invalid_components:
            msg.error(f"Invalid components: {', '.join(invalid_components)}")
            msg.custom(f"Available components: {', '.join(available_tools)}", color.cyan)
            return False
        target_components = tools_to_install
    else:
        target_components = available_tools
    
    success = True
    
    for installer_name, installer_cls in INSTALLERS_MAP.items():
        if config.get(installer_name):
            for tool_name, tool_config in config[installer_name].items():
                if tool_name in target_components:
                    installer = installer_cls(
                        **tool_config,
                        name=tool_name,
                        dry_run=dry_run,
                        force=force,
                        log_file=log_file
                    )
                    try:
                        result = installer.install()
                        success = success and result
                    except Exception as e:
                        logging.error("Unexpected error occurred:")
                        logging.error(traceback.format_exc())
                        msg.error(
                            "An unexpected error occurred. Check logs for details."
                        )
                        success = False

    msg.custom(f"\nDetailed logs written to {log_file}", color.orange)
    
    if success:
        if dry_run:
            msg.custom("\nDry run completed", color.green)
        else:
            msg.custom("\nInstallation completed successfully", color.green)
    else:
        if dry_run:
            msg.custom(
                "Dry run completed with errors. Check install.log for details.",
                color.red
            )
        else:
            msg.custom(
                "Installation completed with errors. "
                "Check install.log for details.", color.red
            )
    
    return success


def list_components() -> None:
    """List all available components."""
    config = load_config()
    
    msg.custom("Available components:", color.cyan)
    
    for installer_name in INSTALLERS_MAP:
        if config.get(installer_name):
            msg.custom(f"\n{installer_name}:", color.yellow)
            for tool_name in config[installer_name]:
                msg.custom(f"  {tool_name}", color.green)


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
  %(prog)s --list                   # List available components
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
            "(use --list to see all available)"
        )
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available components and exit'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_components()
        return
    
    if args.dry_run:
        msg.custom("Dry run mode - No changes will be made", color.green)
    
    success = install_all_tools(
        dry_run=args.dry_run,
        tools_to_install=args.components,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
