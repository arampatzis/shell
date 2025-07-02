#!/usr/bin/env python3
"""
Advanced Dotfiles Installation Script

This script provides a comprehensive solution for managing dotfiles and development 
environment setup. It supports selective installation, dry-run mode, rollback 
capabilities, and detailed logging.
"""
from abc import ABC, abstractmethod
import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import tempfile
import platform
from typing import TextIO
import yaml

from messages import message as msg
from messages import color


@dataclass(kw_only=True)
class Installer(ABC):
    """Base installer class with common functionality."""
    
    name: str = ""
    dry_run: bool = False
    check_cmd: str = ""
    check_path: str = ""
    required_deps: list[str] | None = None
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))
    
    @abstractmethod
    def _install(self) -> bool:
        """Install a tool."""
        pass
    
    def install(self) -> bool:
        """Install a tool from a source to a target."""
        if self._check_installed(self.name):
            return True
        if not self._check_dependencies(self.required_deps):
            return False
        return self._install()
    
    def _check_installed(self, name: str) -> bool:
        """Check if the tool is already installed."""    
        print(f'\n* {self.name}')

        if (self.check_cmd and shutil.which(self.check_cmd)) or self._check_path(name):
            msg.custom(f"    {name} is found in the system.", color.yellow)
            self.logger.warning(f"{name} already installed, skipping")
            return True

        return False
    
    def _check_path(self, name: str) -> bool:
        if self.check_path:
            check_location = Path(self.check_path).expanduser()
            if check_location.exists():
                self.logger.warning(f"{name} already installed (directory check), skipping")
                return True
        return False
    
    def _check_dependencies(self, dependencies: list) -> bool:
        """Check if required dependencies are available."""
        if dependencies is None:
            return True
        missing = [dep for dep in dependencies if not shutil.which(dep)]
        if missing:
            msg.error(f"Missing dependencies: {', '.join(missing)}")
            self.logger.error(f"Missing dependencies: {', '.join(missing)}")
            return False
        return True
    
    def _handle_error(self, error: Exception) -> bool:
        """Handle installation errors."""
        msg.error(f"{self.name} installation failed: {error}")
        msg.error("Check install.log for detailed error information")
        self.logger.error(f"{self.name} installation failed: {error}")
        
        with open('install.log', 'a') as log_file:
            log_file.write(
                f"\n=== {self.name} installation FAILED at {datetime.now()} ===\n"
            )
            log_file.write(f"Error: {error}\n")
        return False


@dataclass(kw_only=True)
class BinaryInstaller(Installer):
    """Handles installation of pre-built binaries from GitHub releases."""
    
    binary_name: str = ""
    repo: str = ""
    version: str = ""
    archive_pattern: str = ""
    required_deps: list[str] = field(default_factory=lambda: ['wget', 'tar'])
    
    def _install(self) -> bool:
        if self.dry_run:
            msg.custom(f"Installing {self.name} from GitHub releases", color.cyan)
            msg.custom(f"    Would download and install {self.binary_name} to ~/.local/bin", color.cyan)
            return True

        msg.custom(f"Installing {self.name} from GitHub releases", color.cyan)
        
        # Create local installation directory
        local_bin_dir = Path.home() / '.local' / 'bin'
        local_bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect architecture
        machine = platform.machine()
        arch_map = {
            'x86_64': 'x86_64',
            'aarch64': 'arm64',
            'arm64': 'arm64'
        }
        arch = arch_map.get(machine, 'x86_64')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Download and extract
                msg.custom(f"   Downloading {self.name} binary...", color.cyan)
                download_url = self.archive_pattern.format(
                    repo=self.repo, version=self.version, arch=arch
                )
                
                with open('install.log', 'a') as log_file:
                    log_file.write(
                        f"\n=== {self.name} download started at {datetime.now()} ===\n"
                    )
                    
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / f'{self.name}.tar.gz'),
                        download_url
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== {self.name} extraction started ===\n")
                    subprocess.run([
                        'tar', '-xzf', f'{self.name}.tar.gz'
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Find and copy binary
                msg.custom(f"   Installing {self.name} to ~/.local/bin...", color.cyan)
                return self._find_and_copy_binary(
                    temp_path,
                    local_bin_dir,
                    log_file
                )
                
            except subprocess.CalledProcessError as e:
                return self._handle_error(e)
            except Exception as e:
                return self._handle_error(e)
    
    def _find_and_copy_binary(
        self,
        temp_path: Path,
        target_dir: Path,
        log_file: TextIO,
    ) -> bool:
        """Find the binary in extracted files and copy to target directory."""
        # Look for binary in extracted directories
        binary_path = None
        for item in temp_path.rglob(self.binary_name):
            if item.is_file() and item.stat().st_mode & 0o111:  # Check if executable
                binary_path = item
                break
        
        if not binary_path:
            raise FileNotFoundError(f"{self.binary_name} binary not found in downloaded archive")
        
        target_binary = target_dir / self.binary_name
        shutil.copy2(binary_path, target_binary)
        target_binary.chmod(0o755)
        
        msg.custom(f"   {self.name} installed successfully to ~/.local/bin", color.green)
        msg.custom("   Detailed logs written to install.log", color.yellow)
        
        with open('install.log', 'a') as log_file:
            log_file.write(
                f"\n=== {self.name} installation completed successfully "
                "at {datetime.now()} ===\n"
            )
        
        return True
    

@dataclass(kw_only=True)
class ScriptInstaller(Installer):
    """Handles installation from git repositories with installer scripts."""

    script_type: str = ""
    repo_url: str = ""
    target_dir: str = ""
    installer_script: str = ""
    installer_args: list = field(default_factory=list)
    script_url: str = ""
    required_deps: list[str] = field(default_factory=lambda: ['git'])
    
    def _install(self) -> bool:
        """
        Install a tool using script-based installation.
        """
        if self.dry_run:
            if self.script_type == 'git_clone':
                msg.custom(f"Installing {self.name} from git repository", color.cyan)
                msg.custom(f"    Would clone {self.repo_url} to {self.target_dir}", color.cyan)
                msg.custom(f"    Would run installer script: {self.installer_script}", color.cyan)
            elif self.script_type == 'direct_script':
                msg.custom(f"Installing {self.name} from script", color.cyan)
                msg.custom(f"    Would download and run script from: {self.script_url}", color.cyan)
            return True
        
        if self.script_type == 'git_clone':
            return self._install_git_clone_script()
        elif self.script_type == 'direct_script':
            return self._install_direct_script()
        else:
            raise ValueError(f"Unknown script_type: {self.script_type}")
    
    def _install_git_clone_script(self) -> bool:
        """Install using git clone + installer script pattern."""
        msg.custom(f"Installing {self.name} from git repository", color.cyan)
        
        # Determine installation directory
        install_dir = Path(self.target_dir)
        
        try:
            # Clone repository
            msg.custom(f"   Cloning {self.name} repository...", color.cyan)
            with open('install.log', 'a') as log_file:
                log_file.write(f"\n=== {self.name} git clone started at {datetime.now()} ===\n")
                
                subprocess.run([
                    'git', 'clone', '--depth', '1',
                    self.repo_url, str(install_dir)
                ], check=True, stdout=log_file, stderr=log_file)
            
            # Run installer script
            msg.custom(f"   Running {self.name} installer...", color.cyan)
            installer_path = install_dir / self.installer_script
            
            if not installer_path.exists():
                raise FileNotFoundError(f"Installer script not found: {installer_path}")
            
            # Prepare installer command
            install_cmd = ['bash', str(installer_path)]
            if self.installer_args:
                install_cmd.extend(self.installer_args)
            
            with open('install.log', 'a') as log_file:
                log_file.write(f"\n=== {self.name} installer started ===\n")
                log_file.write(f"Command: {' '.join(install_cmd)}\n")
                
                subprocess.run(install_cmd, check=True, stdout=log_file, stderr=log_file)
            
            msg.custom(f"   {self.name} installed successfully", color.green)
            msg.custom("   Detailed logs written to install.log", color.yellow)
            
            with open('install.log', 'a') as log_file:
                log_file.write(f"\n=== {self.name} installation completed successfully at {datetime.now()} ===\n")
            
            return True
            
        except subprocess.CalledProcessError as e:
            return self._handle_error(e)
        except Exception as e:
            return self._handle_error(e)
    
    def _install_direct_script(self) -> bool:
        """Install using direct script download and execution."""
        msg.custom(f"Installing {self.name} from script", color.cyan)
        
        try:
            # Download and execute script
            msg.custom(f"   Downloading and running {self.name} installer...", color.cyan)
            
            # Prepare installer command
            install_cmd = ['bash', '-c', f'curl -fsSL {self.script_url} | bash']
            
            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} direct script installation "
                    "started at {datetime.now()} ===\n"
                )
                log_file.write(f"Script URL: {self.script_url}\n")
                
                subprocess.run(install_cmd, check=True, stdout=log_file, stderr=log_file)
            
            msg.custom(f"   {self.name} installed successfully", color.green)
            msg.custom("   Detailed logs written to install.log", color.yellow)
            
            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} installation completed successfully "
                    "at {datetime.now()} ===\n"
                )
            
            return True
            
        except subprocess.CalledProcessError as e:
            return self._handle_error(e)
        except Exception as e:
            return self._handle_error(e)


@dataclass(kw_only=True)
class SymlinkerInstaller(Installer):
    """Handles file and directory symlinking operations."""
    
    source: str = ""
    target: str = ""
    expand: bool = False
    backup_dir: Path = field(default_factory=lambda: Path('.install.bak'))
    operations_log: list = field(default_factory=list)
    required_deps: list[str] = field(default_factory=list)  # No external dependencies
    
    def __post_init__(self):
        """Initialize backup directory after dataclass initialization."""
        # Ensure backup directory exists
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
    
    def _install(self) -> bool:
        """Install files using symlinking."""
        msg.custom(f"Installing {self.name}", color.cyan)
        
        source_path = Path(self.source)
        target_path = Path(self.target).expanduser()
        
        if not source_path.exists():
            msg.error(f"    Source directory {source_path} not found")
            return False
        
        # Handle expand pattern - contents of source go into target
        if self.expand:
            success = True
            for item in source_path.iterdir():
                target = target_path / item.name
                if not self.create_symlink(item, target):
                    success = False
            return success
        # Handle direct mapping - source to target
        else:
            return self.create_symlink(source_path, target_path)
    
    def backup_file(self, path: Path) -> Optional[Path]:
        """Create backup of existing file/directory."""
        if not path.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        backup_name = f"{path.name}.{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        if self.dry_run:
            msg.warning(f"    [DRY RUN] Would backup {path.name}")
            self.logger.info(f"[DRY RUN] Would backup {path} to {backup_path}")
            return backup_path
        
        try:
            if path.is_symlink():
                # For symlinks, copy the link itself, not what it points to
                backup_path.symlink_to(path.readlink())
                msg.warning(f"    Backed up existing symlink {path.name}")
                self.logger.info(f"Backed up symlink {path} to {backup_path}")
            elif path.is_dir():
                # Don't follow symlinks to avoid infinite loops
                shutil.copytree(path, backup_path, symlinks=True)
                msg.warning(f"    Backed up existing directory {path.name}")
                self.logger.info(f"Backed up directory {path} to {backup_path}")
            else:
                shutil.copy2(path, backup_path)
                msg.warning(f"    Backed up existing file {path.name}")
                self.logger.info(f"Backed up file {path} to {backup_path}")
            
            return backup_path
        except OSError as e:
            msg.error(f"    Failed to backup {path.name}: {e}")
            self.logger.error(f"Failed to backup {path}: {e}")
            return None
    
    def create_symlink(self, source: Path, target: Path) -> bool:
        """Create symbolic link with proper error handling."""
        source = source.expanduser().resolve()
        target_expanded = target.expanduser()
        
        # Log to file only
        self.logger.info(f"Creating symlink: {target_expanded} -> {source}")
        
        # Create a user-friendly target path display (replace home directory with ~)
        target_display = str(target_expanded).replace(str(Path.home()), "~")
        source_display = str(source).replace(str(Path.home()), "~")
        
        if self.dry_run:
            msg.custom(f"    {target_display} -> {source_display}", color.yellow)
            return True
        else:
            msg.custom(f"    Linking {target_display}", color.yellow)
        
        # Remove existing file/symlink
        if target_expanded.exists() or target_expanded.is_symlink():
            # Check if existing symlink already points to our source
            should_backup = True
            if target_expanded.is_symlink():
                try:
                    existing_target = target_expanded.readlink().resolve()
                    if existing_target == source:
                        should_backup = False
                        msg.warning(f"    Symlink {target_expanded.name} already points to source, skipping backup")
                        self.logger.info(f"Symlink {target_expanded} already points to {source}, skipping backup")
                except (OSError, RuntimeError):
                    # If we can't resolve the symlink, backup anyway to be safe
                    should_backup = True
            
            if should_backup:
                backup_path = self.backup_file(target_expanded)
                if backup_path:
                    self.operations_log.append({
                        'action': 'backup',
                        'original': str(target_expanded),
                        'backup': str(backup_path)
                    })
            
            if target_expanded.is_symlink():
                target_expanded.unlink()
            elif target_expanded.is_dir():
                shutil.rmtree(target_expanded)
            else:
                target_expanded.unlink()
        
        # Create parent directory if needed (resolve parent path to avoid issues)
        parent_dir = target_expanded.parent.resolve()
        parent_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            target_expanded.symlink_to(source)
            self.operations_log.append({
                'action': 'symlink',
                'source': str(source),
                'target': str(target_expanded)
            })
            return True
        except OSError as e:
            msg.error(f"    Failed to create symlink {target_expanded.name}: {e}")
            self.logger.error(f"Failed to create symlink {target_expanded} -> {source}: {e}")
            return False
    
    def install_dotfiles_from_dir(self, source_dir: Path, description: str = "files") -> bool:
        """Install dotfiles from a source directory."""
        if not source_dir.exists():
            msg.error(f"{description} directory {source_dir} not found")
            self.logger.error(f"{description} directory {source_dir} not found")
            return False
        
        msg.custom(f"Installing {description}", color.cyan)
        
        success = True
        for dotfile in source_dir.glob('.*'):
            if dotfile.is_file():
                target = Path.home() / dotfile.name
                if not self.create_symlink(dotfile, target):
                    success = False
        
        return success
    
    def install_config_from_dir(self, source_dir: Path, description: str = "config files") -> bool:
        """Install config files from a source directory to ~/.config."""
        if not source_dir.exists():
            msg.error(f"{description} directory {source_dir} not found")
            self.logger.error(f"{description} directory {source_dir} not found")
            return False
        
        msg.custom(f"Installing {description}", color.cyan)
        
        config_dir = Path.home() / '.config'
        success = True
        
        for item in source_dir.iterdir():
            target = config_dir / item.name
            if not self.create_symlink(item, target):
                success = False
        
        return success


@dataclass(kw_only=True)
class SourceInstaller(Installer):
    """Handles installation from source code."""
    
    repo: str = ""
    version: str = ""
    archive_pattern: str = ""
    binary_name: str = ""
    build_deps: list = field(default_factory=list)
    configure_args: list = field(default_factory=list)
    required_deps: list[str] = field(default_factory=lambda: ['wget', 'tar', 'make', 'gcc'])
    
    def _install(self) -> bool:
        """Install a tool from source code."""
        # Check build dependencies
        if self.build_deps:
            missing = [dep for dep in self.build_deps if not shutil.which(dep)]
            if missing:
                msg.error(f"Missing build dependencies for {self.name}: {', '.join(missing)}")
                self.logger.error(f"Missing {self.name} build dependencies: {', '.join(missing)}")
                return False
        
        if self.dry_run:
            msg.custom(f"Installing {self.name} from source", color.cyan)
            msg.custom(f"    Would download source from: {self.repo}", color.cyan)
            msg.custom(f"    Would configure, build and install to ~/.local", color.cyan)
            return True
        
        msg.custom(f"Installing {self.name} from source", color.cyan)
        
        # Create local installation directory
        local_bin_dir = Path.home() / '.local' / 'bin'
        local_bin_dir.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Download source
                msg.custom(f"   Downloading {self.name} source...", color.cyan)
                download_url = self.archive_pattern.format(
                    repo=self.repo, version=self.version
                )
                
                # Determine archive format from URL
                if '.tar.bz2' in download_url:
                    archive_name = f'{self.name}.tar.bz2'
                    tar_flags = '-xjf'
                else:
                    archive_name = f'{self.name}.tar.gz'
                    tar_flags = '-xzf'
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} source download started at {datetime.now()} ===\n")
                    
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / archive_name),
                        download_url
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== {self.name} source extraction started ===\n")
                    subprocess.run([
                        'tar', tar_flags, archive_name
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Find extracted source directory
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name.startswith(self.name)]
                if not extracted_dirs:
                    raise RuntimeError(f"Could not find extracted {self.name} source directory")
                
                source_dir = extracted_dirs[0]
                
                # Configure
                msg.custom(f"   Configuring {self.name}...", color.cyan)
                configure_cmd = ['./configure', f'--prefix={Path.home()}/.local']
                if self.configure_args:
                    configure_cmd.extend(self.configure_args)
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} configure started ===\n")
                    log_file.write(f"Command: {' '.join(configure_cmd)}\n")
                    
                    subprocess.run(configure_cmd, check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                # Build
                msg.custom(f"   Building {self.name}...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} build started ===\n")
                    
                    subprocess.run(['make'], check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                # Install
                msg.custom(f"   Installing {self.name} to ~/.local...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} install started ===\n")
                    
                    subprocess.run(['make', 'install'], check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                msg.custom(f"   {self.name} installed successfully to ~/.local/bin", color.green)
                msg.custom("   Detailed logs written to install.log", color.yellow)
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} installation completed successfully at {datetime.now()} ===\n")
                
                return True
                
            except subprocess.CalledProcessError as e:
                return self._handle_error(e)
            except Exception as e:
                return self._handle_error(e)


def load_config() -> dict:
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
    components: Optional[List[str]] = None
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
    
    # Install binary tools
    if config.get('binary_tools'):
        for tool_name, tool_config in config['binary_tools'].items():
            if tool_name in target_components:
                installer = BinaryInstaller(**tool_config, dry_run=dry_run)
                if not installer.install():
                    success = False
    
    # Install script tools
    if config.get('script_tools'):
        for tool_name, tool_config in config['script_tools'].items():
            if tool_name in target_components:
                installer = ScriptInstaller(**tool_config, dry_run=dry_run)
                if not installer.install():
                    success = False
    
    # Install source tools
    if config.get('source_tools'):
        for tool_name, tool_config in config['source_tools'].items():
            if tool_name in target_components:
                installer = SourceInstaller(**tool_config, dry_run=dry_run)
                if not installer.install():
                    success = False
    
    # Install dotfiles
    if config.get('dotfile_configs'):
        for tool_name, tool_config in config['dotfile_configs'].items():
            if tool_name in target_components:
                installer = SymlinkerInstaller(**tool_config, dry_run=dry_run)
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
            msg.custom("Dry run completed with errors. Check install.log for details.", color.yellow)
        else:
            msg.custom("Installation completed with errors. Check install.log for details.", color.yellow)
    
    return success


def list_components():
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


def main():
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Advanced Dotfiles Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Install all components
  %(prog)s --dry-run                # Show what would be installed
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
        '--components',
        nargs='+',
        help="Specific components to install (use --list-components to see all available)"
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
        msg.custom("DRY RUN MODE - No changes will be made", color.yellow)
    
    success = install_all_tools(dry_run=args.dry_run, components=args.components)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
