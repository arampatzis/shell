#!/usr/bin/env python3
"""
Advanced Dotfiles Installation Script

This script provides a comprehensive solution for managing dotfiles and development 
environment setup. It supports selective installation, dry-run mode, rollback 
capabilities, and detailed logging.
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from messages import message as msg
from messages import color


class RollbackManager:
    """Handles rollback operations for the installer."""
    
    def __init__(self, operations_file: str = "install_operations.json"):
        self.operations_file = Path(operations_file)
        self.logger = logging.getLogger(__name__)
    
    def rollback_installation(self) -> bool:
        """Rollback the last installation."""
        if not self.operations_file.exists():
            self.logger.error("No operations log found. Cannot rollback.")
            return False
        
        try:
            with open(self.operations_file, 'r') as f:
                operations = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Failed to load operations log: {e}")
            return False
        
        self.logger.info("Starting rollback...")
        success = True
        
        # Process operations in reverse order
        for operation in reversed(operations):
            if operation['action'] == 'symlink':
                success &= self._remove_symlink(Path(operation['target']))
            elif operation['action'] == 'backup':
                success &= self._restore_backup(
                    Path(operation['backup']), 
                    Path(operation['original'])
                )
        
        if success:
            self.logger.info("Rollback completed successfully")
            # Remove operations log after successful rollback
            self.operations_file.unlink()
        else:
            self.logger.error("Rollback completed with errors")
        
        return success
    
    def _remove_symlink(self, symlink_path: Path) -> bool:
        """Remove a symlink created during installation."""
        try:
            if symlink_path.is_symlink():
                symlink_path.unlink()
                self.logger.info(f"Removed symlink: {symlink_path}")
                return True
            elif symlink_path.exists():
                self.logger.warning(f"Path exists but is not a symlink: {symlink_path}")
                return False
            else:
                self.logger.info(f"Symlink already removed: {symlink_path}")
                return True
        except OSError as e:
            self.logger.error(f"Failed to remove symlink {symlink_path}: {e}")
            return False
    
    def _restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a file from backup."""
        try:
            if not backup_path.exists():
                self.logger.warning(f"Backup file not found: {backup_path}")
                return False
            
            # Remove current file/directory if it exists
            if original_path.exists():
                if original_path.is_dir():
                    shutil.rmtree(original_path)
                else:
                    original_path.unlink()
            
            # Restore from backup
            if backup_path.is_dir():
                shutil.copytree(backup_path, original_path)
            else:
                shutil.copy2(backup_path, original_path)
            
            self.logger.info(f"Restored {original_path} from backup")
            return True
        except OSError as e:
            self.logger.error(f"Failed to restore {original_path} from backup: {e}")
            return False


class DotfilesInstaller:
    """Advanced dotfiles installer with comprehensive features."""
    
    # Hardcoded component configuration - no external config files needed
    COMPONENTS = {
        'oh_my_bash_installation': {
            'source_dir': '',  # No source dir for installation check
            'description': 'Oh My Bash installation check'
        },
        'dotfiles': {
            'source_dir': 'data/dotfiles',
            'description': 'Dotfiles (.bashrc, .vimrc, etc.)'
        },
        'oh_my_bash_configuration': {
            'source_dir': 'data/oh-my-bash', 
            'description': 'Oh My Bash configuration'
        },
        'config': {
            'source_dir': 'data/config',
            'description': 'Configuration files (.config directory)'
        },
        'vifm': {
            'source_dir': '',  # External installation, no source dir
            'description': 'Vi file manager installation'
        },
        'lazygit': {
            'source_dir': '',  # External installation, no source dir
            'description': 'Git UI terminal application'
        },
        'ripgrep': {
            'source_dir': '',  # External installation, no source dir
            'description': 'Fast grep alternative written in Rust'
        },
        'fzf': {
            'source_dir': '',  # External installation, no source dir
            'description': 'Fuzzy finder installation'
        }
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.home = Path.home()
        self.operations_log = []
        self.backup_dir = Path('.install.bak')
        
        # Setup logging
        self._setup_logging()
        
        # Setup backup directory
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self):
        """Configure logging system."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        # Only log to file, not to console (we'll use the messages module for console)
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('install.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        dependencies = ['git', 'bash']
        missing = []
        
        for dep in dependencies:
            if not shutil.which(dep):
                missing.append(dep)
        
        if missing:
            msg.error(f"Missing dependencies: {', '.join(missing)}")
            self.logger.error(f"Missing dependencies: {', '.join(missing)}")
            return False
        
        return True
    
    def _check_vifm_build_dependencies(self) -> bool:
        """Check if build dependencies for vifm are available."""
        build_deps = ['wget', 'tar', 'make', 'gcc']
        missing = []
        
        for dep in build_deps:
            if not shutil.which(dep):
                missing.append(dep)
        
        if missing:
            msg.error(f"Missing build dependencies for vifm: {', '.join(missing)}")
            msg.error("Please install build tools:")
            msg.error("  Ubuntu/Debian: sudo apt install build-essential libncurses-dev")
            msg.error("  CentOS/RHEL: sudo yum groupinstall 'Development Tools' && sudo yum install ncurses-devel")
            msg.error("  Arch Linux: sudo pacman -S base-devel ncurses")
            self.logger.error(f"Missing vifm build dependencies: {', '.join(missing)}")
            return False
        
        return True
    
    def _backup_file(self, path: Path) -> Optional[Path]:
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
    
    def _create_symlink(self, source: Path, target: Path) -> bool:
        """Create symbolic link with proper error handling."""
        source = source.expanduser().resolve()
        target_expanded = target.expanduser()
        
        # Log to file only
        self.logger.info(f"Creating symlink: {target_expanded} -> {source}")
        
        # Create a user-friendly target path display (replace home directory with ~)
        target_display = str(target_expanded).replace(str(self.home), "~")
        
        if self.dry_run:
            msg.custom(f"    [DRY RUN] Would link {target_display} -> {source}", color.yellow)
            return True
        else:
            msg.custom(f"    Linking {target_display}", color.cyan)
        
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
                backup_path = self._backup_file(target_expanded)
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
    
    def install_dotfiles(self) -> bool:
        """Install dotfiles to home directory."""
        source_dir = Path(self.COMPONENTS['dotfiles']['source_dir'])
        
        if not source_dir.exists():
            msg.error(f"Dotfiles directory {source_dir} not found")
            self.logger.error(f"Dotfiles directory {source_dir} not found")
            return False
        
        print('\n* dotfiles')
        msg.custom("Installing dotfiles", color.cyan)
        
        success = True
        for dotfile in source_dir.glob('.*'):
            if dotfile.is_file():
                target = self.home / dotfile.name
                if not self._create_symlink(dotfile, target):
                    success = False
        
        return success
    
    def install_oh_my_bash_installation(self) -> bool:
        """Check Oh My Bash installation."""
        
        print('\n* oh-my-bash installation')
        
        url = "https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh"
        
        # Check if oh-my-bash is installed
        omb_dir = self.home / '.oh-my-bash'
        if not omb_dir.exists():
            msg.error("    Oh My Bash not found. Please install it first:")
            msg.error(
                f'    bash -c "$(wget {url} -O -)"'
            )
            self.logger.error("Oh My Bash not found")
            return False
        else:
            msg.warning("    oh-my-bash is found in the system.")
        
        return True
    
    def install_oh_my_bash_configuration(self) -> bool:
        """Install Oh My Bash configuration."""
        
        print('\n* oh-my-bash configuration')
        msg.custom("Installing Oh My Bash configuration", color.cyan)
        
        # Install configuration
        return self._install_oh_my_bash_configuration()
    
    def _install_oh_my_bash_configuration(self) -> bool:
        """Install Oh My Bash configuration files."""
        source_dir = Path(self.COMPONENTS['oh_my_bash_configuration']['source_dir'])
        
        if not source_dir.exists():
            msg.error(f"    Oh My Bash config directory {source_dir} not found")
            self.logger.error(f"Oh My Bash config directory {source_dir} not found")
            return False
        
        omb_dir = self.home / '.oh-my-bash'
        
        # Link bashrc
        bashrc_source = source_dir / '.bashrc'
        bashrc_target = self.home / '.bashrc'
        if bashrc_source.exists():
            if not self._create_symlink(bashrc_source, bashrc_target):
                return False
        
        # Link custom directory
        custom_source = source_dir / 'custom'
        custom_target = omb_dir / 'custom'
        if custom_source.exists():
            if not self._create_symlink(custom_source, custom_target):
                return False
        
        return True
    
    def install_config_files(self) -> bool:
        """Install configuration files."""
        source_dir = Path(self.COMPONENTS['config']['source_dir'])
        
        if not source_dir.exists():
            msg.error(f"Config directory {source_dir} not found")
            self.logger.error(f"Config directory {source_dir} not found")
            return False
        
        print('\n* config')
        msg.custom("Installing configuration files", color.cyan)
        
        config_dir = self.home / 'config'
        config_dir.mkdir(exist_ok=True)
        
        success = True
        for item in source_dir.iterdir():
            if item.is_dir():
                target = config_dir / item.name
                if not self._create_symlink(item, target):
                    success = False
        
        return success
    
    def install_vifm(self) -> bool:
        """Install vifm file manager from source."""
        print('\n* vifm')
        
        # Check if vifm is already installed
        if shutil.which('vifm'):
            msg.warning("   vifm already installed, skipping")
            self.logger.warning("vifm already installed, skipping")
            return True
        
        # Check build dependencies
        if not self._check_vifm_build_dependencies():
            return False
        
        if self.dry_run:
            msg.custom("   [DRY RUN] Would install vifm from source", color.yellow)
            return True
        
        msg.custom("Installing vifm from source", color.cyan)
        
        # Create local installation directory
        local_dir = self.home / '.local'
        local_dir.mkdir(exist_ok=True)
        
        # Create temporary build directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vifm_source = temp_path / 'vifm'
            
            try:
                # Download and extract vifm source
                msg.custom("   Downloading vifm source...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== vifm download started at {datetime.now()} ===\n")
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / 'vifm.tar.bz2'),
                        'https://github.com/vifm/vifm/releases/download/v0.13/vifm-0.13.tar.bz2'
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== vifm extraction started ===\n")
                    subprocess.run([
                        'tar', '-xjf', 'vifm.tar.bz2'
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Find the extracted directory (should be vifm-0.13)
                extracted_dirs = [
                    d for d in temp_path.iterdir() 
                    if d.is_dir() 
                    and d.name.startswith('vifm-')
                    and d.name.endswith('.tar.bz2')
                ]
                if not extracted_dirs:
                    raise RuntimeError("Could not find extracted vifm directory")
                
                vifm_source = extracted_dirs[0]
                
                # Configure vifm
                msg.custom(
                    "   Configuring vifm...",
                    color.cyan
                )
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== vifm configure started ===\n")
                    subprocess.run([
                        './configure', f'--prefix={local_dir}'
                    ], check=True, cwd=vifm_source, stdout=log_file, stderr=log_file)
                
                # Build vifm
                msg.custom(
                    "   Building vifm... (this may take a few minutes)",
                    color.cyan
                )
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== vifm build started ===\n")
                    subprocess.run(
                        [
                            'make',
                            'install',
                            f'--prefix={local_dir}'
                        ],
                        check=True,
                        cwd=vifm_source, stdout=log_file, stderr=log_file)
                
                # Install vifm
                msg.custom("   Installing vifm to ~/.local/bin...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== vifm install started ===\n")
                    subprocess.run(
                        [
                            'make',
                            'install',
                            f'--prefix={local_dir}'
                        ],
                        check=True, cwd=vifm_source, stdout=log_file, stderr=log_file)
                
                msg.custom("   vifm installed successfully to ~/.local/bin", color.green)
                msg.custom("   Detailed build logs written to install.log", color.yellow)
                
                # Log completion
                with open('install.log', 'a') as log_file:
                    log_file.write(
                        f"\n=== vifm installation completed successfully "
                        f"at {datetime.now()} ===\n"
                        f"vifm installed to {local_dir}/bin/vifm"
                    )
                
                return True
            except subprocess.CalledProcessError as e:
                msg.error(f"vifm installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"vifm installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(
                        f"\n=== vifm installation FAILED at {datetime.now()} ===\n"
                        f"Error: {e}\n"
                    )
                    log_file.write(f"Error: {e}\n")
                return False
            except Exception as e:
                msg.error(f"vifm installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"vifm installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(
                        f"\n=== vifm installation FAILED at {datetime.now()} ===\n"
                        f"Error: {e}\n"
                    )
                return False
    
    def install_lazygit(self) -> bool:
        """Install lazygit from pre-built binary."""
        
        lazygit_url = (
            f"https://github.com/jesseduffield/lazygit/releases/download/v0.44.1/lazygit_0.44.1_Linux_{arch}.tar.gz"
        )
        
        print('\n* lazygit')
        
        # Check if lazygit is already installed
        if shutil.which('lazygit'):
            msg.warning("   lazygit already installed, skipping")
            self.logger.warning("lazygit already installed, skipping")
            return True
        
        # Check basic dependencies (no build tools needed)
        basic_deps = ['wget', 'tar']
        missing = []
        for dep in basic_deps:
            if not shutil.which(dep):
                missing.append(dep)
        
        if missing:
            msg.error(f"Missing dependencies for lazygit: {', '.join(missing)}")
            self.logger.error(f"Missing lazygit dependencies: {', '.join(missing)}")
            return False
        
        if self.dry_run:
            msg.custom("   [DRY RUN] Would install lazygit from GitHub releases", color.yellow)
            return True
        
        msg.custom("Installing lazygit from GitHub releases", color.cyan)
        
        # Create local installation directory
        local_dir = self.home / '.local'
        local_bin_dir = local_dir / 'bin'
        local_bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary download directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Download lazygit binary
                msg.custom("   Downloading lazygit binary...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== lazygit download started at {datetime.now()} ===\n")
                    
                    # Detect architecture and OS
                    import platform
                    machine = platform.machine()
                    if machine == 'x86_64':
                        arch = 'x86_64'
                    elif machine == 'aarch64' or machine == 'arm64':
                        arch = 'arm64'
                    else:
                        arch = 'x86_64'  # Default fallback
                    
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / 'lazygit.tar.gz'),
                        lazygit_url
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== lazygit extraction started ===\n")
                    subprocess.run([
                        'tar', '-xzf', 'lazygit.tar.gz'
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Copy binary to ~/.local/bin
                msg.custom("   Installing lazygit to ~/.local/bin...", color.cyan)
                lazygit_binary = temp_path / 'lazygit'
                target_binary = local_bin_dir / 'lazygit'
                
                if not lazygit_binary.exists():
                    raise FileNotFoundError("lazygit binary not found in downloaded archive")
                
                shutil.copy2(lazygit_binary, target_binary)
                target_binary.chmod(0o755)  # Make executable
                
                msg.custom("   lazygit installed successfully to ~/.local/bin", color.green)
                msg.custom("   Detailed logs written to install.log", color.yellow)
                
                # Log completion
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== lazygit installation completed successfully at {datetime.now()} ===\n")
                
                return True
            except subprocess.CalledProcessError as e:
                msg.error(f"lazygit installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"lazygit installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== lazygit installation FAILED at {datetime.now()} ===\n")
                    log_file.write(f"Error: {e}\n")
                return False
            except Exception as e:
                msg.error(f"lazygit installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"lazygit installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== lazygit installation FAILED at {datetime.now()} ===\n")
                    log_file.write(f"Error: {e}\n")
                return False
    
    def install_ripgrep(self) -> bool:
        """Install ripgrep from pre-built binary."""
        print('\n* ripgrep')
        
        # Check if ripgrep is already installed
        if shutil.which('rg'):
            msg.warning("   ripgrep already installed, skipping")
            self.logger.warning("ripgrep already installed, skipping")
            return True
        
        # Check basic dependencies (no build tools needed)
        basic_deps = ['wget', 'tar']
        missing = []
        for dep in basic_deps:
            if not shutil.which(dep):
                missing.append(dep)
        
        if missing:
            msg.error(f"Missing dependencies for ripgrep: {', '.join(missing)}")
            self.logger.error(f"Missing ripgrep dependencies: {', '.join(missing)}")
            return False
        
        if self.dry_run:
            msg.custom("   [DRY RUN] Would install ripgrep from GitHub releases", color.yellow)
            return True
        
        msg.custom("Installing ripgrep from GitHub releases", color.cyan)
        
        # Create local installation directory
        local_dir = self.home / '.local'
        local_bin_dir = local_dir / 'bin'
        local_bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary download directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Download ripgrep binary
                msg.custom("   Downloading ripgrep binary...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== ripgrep download started at {datetime.now()} ===\n")
                    
                    # Detect architecture and OS
                    import platform
                    machine = platform.machine()
                    if machine == 'x86_64':
                        arch_target = 'x86_64-unknown-linux-musl'
                    elif machine == 'aarch64' or machine == 'arm64':
                        arch_target = 'aarch64-unknown-linux-gnu'
                    else:
                        arch_target = 'x86_64-unknown-linux-musl'  # Default fallback
                    
                    # Use a recent stable release
                    # TODO: In the future, use GitHub API to get the actual latest version
                    version = "14.1.0"
                    ripgrep_url = f"https://github.com/BurntSushi/ripgrep/releases/download/{version}/ripgrep-{version}-{arch_target}.tar.gz"
                    
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / 'ripgrep.tar.gz'),
                        ripgrep_url
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== ripgrep extraction started ===\n")
                    subprocess.run([
                        'tar', '-xzf', 'ripgrep.tar.gz'
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Find the extracted directory and binary
                msg.custom("   Installing ripgrep to ~/.local/bin...", color.cyan)
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name.startswith('ripgrep-')]
                if not extracted_dirs:
                    raise RuntimeError("Could not find extracted ripgrep directory")
                
                ripgrep_dir = extracted_dirs[0]
                ripgrep_binary = ripgrep_dir / 'rg'
                target_binary = local_bin_dir / 'rg'
                
                if not ripgrep_binary.exists():
                    raise FileNotFoundError("ripgrep binary (rg) not found in downloaded archive")
                
                shutil.copy2(ripgrep_binary, target_binary)
                target_binary.chmod(0o755)  # Make executable
                
                msg.custom("   ripgrep installed successfully to ~/.local/bin", color.green)
                msg.custom("   Detailed logs written to install.log", color.yellow)
                
                # Log completion
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== ripgrep installation completed successfully at {datetime.now()} ===\n")
                
                return True
            except subprocess.CalledProcessError as e:
                msg.error(f"ripgrep installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"ripgrep installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== ripgrep installation FAILED at {datetime.now()} ===\n")
                    log_file.write(f"Error: {e}\n")
                return False
            except Exception as e:
                msg.error(f"ripgrep installation failed: {e}")
                msg.error("Check install.log for detailed error information")
                self.logger.error(f"ripgrep installation failed: {e}")
                
                # Log the error details
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== ripgrep installation FAILED at {datetime.now()} ===\n")
                    log_file.write(f"Error: {e}\n")
                return False
    
    def install_fzf(self) -> bool:
        """Install fzf fuzzy finder."""
        fzf_dir = self.home / '.fzf'
        
        print('\n* fzf')
        
        if fzf_dir.exists():
            msg.warning("   .fzf already exists in home directory. Aborting installation...")
            self.logger.warning("fzf already installed, skipping")
            return True
        
        if self.dry_run:
            msg.custom("   [DRY RUN] Would install fzf", color.yellow)
            return True
        
        msg.custom("Installing fzf", color.cyan)
        
        try:
            # Clone fzf repository
            msg.inseparator('Start git clone', n=60, sep='-', clr=color.orange)
            subprocess.run([
                'git', 'clone', '--depth', '1',
                'https://github.com/junegunn/fzf.git',
                str(fzf_dir)
            ], check=True)
            msg.inseparator('End git clone', n=60, sep='-', clr=color.orange)
            
            print('\n   * Install fzf: \n')
            
            # Run fzf installer
            installer = fzf_dir / 'install'
            msg.inseparator('Start fzf installer (external script)', n=60, sep='-', clr=color.orange)
            subprocess.run([
                'bash', str(installer),
                '--no-zsh', '--no-fish',
                '--key-bindings', '--completion', '--update-rc'
            ], check=True)
            msg.inseparator('End fzf installer', n=60, sep='-', clr=color.orange)
            
            return True
        except subprocess.CalledProcessError as e:
            msg.error(f"fzf installation failed: {e}")
            self.logger.error(f"fzf installation failed: {e}")
            return False
    
    def save_operations_log(self):
        """Save operations log for potential rollback."""
        if self.dry_run:
            return
        
        log_file = Path('install_operations.json')
        with open(log_file, 'w') as f:
            json.dump(self.operations_log, f, indent=2)
        
        # Log to file only (no console spam)
        self.logger.info(f"Operations log saved to {log_file}")
    
    def install_selected_components(
        self,
        components: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> bool:
        """Install selected components."""
        if not self._check_dependencies():
            return False
        
        available_components = {
            'oh_my_bash_installation': self.install_oh_my_bash_installation,
            'dotfiles': self.install_dotfiles,
            'oh_my_bash_configuration': self.install_oh_my_bash_configuration,
            'config': self.install_config_files,
            'vifm': self.install_vifm,
            'lazygit': self.install_lazygit,
            'ripgrep': self.install_ripgrep,
            'fzf': self.install_fzf
        }
        
        if components is None:
            components = list(available_components.keys())
        
        # Validate component names
        invalid_components = set(components) - set(available_components.keys())
        if invalid_components:
            msg.error(f"Invalid components: {', '.join(invalid_components)}")
            msg.custom(f"Available components: {', '.join(available_components.keys())}", color.cyan)
            self.logger.error(f"Invalid components: {', '.join(invalid_components)}")
            return False
        
        success = True
        for component in components:
            # Log to file only
            self.logger.info(f"Installing component: {component}")
            if not available_components[component]():
                success = False
                msg.error(f"Failed to install component: {component}")
                self.logger.error(f"Failed to install component: {component}")
        
        # Save operations log
        self.save_operations_log()
        
        if success:
            if self.dry_run:
                msg.custom(f"\nDry run completed", color.cyan)
            else:
                msg.custom(f"\nInstallation completed! Backup files stored in {self.backup_dir}", color.cyan)
        else:
            if self.dry_run:
                msg.custom("Dry run completed with errors. Check install.log for details.", color.yellow)
            else:
                msg.custom("Installation completed with errors. Check install.log for details.", color.yellow)
        
        return success


def rollback_installation():
    """Rollback the last installation."""
    rollback_manager = RollbackManager()
    success = rollback_manager.rollback_installation()
    sys.exit(0 if success else 1)


def main():
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Advanced Dotfiles Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Install all components
  %(prog)s --dry-run                # Show what would be installed
  %(prog)s --components dotfiles oh_my_bash_configuration  # Install specific components
  %(prog)s --list-components        # List available components
  %(prog)s --rollback               # Rollback last installation
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
        help=(
            "Specific components to install ",
            "(oh_my_bash_installation, dotfiles, oh_my_bash_configuration, config, vifm, lazygit, fzf)"
        )
    )
    
    parser.add_argument(
        '--list-components',
        action='store_true',
        help='List available components and exit'
    )
    
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback the last installation'
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_installation()
        return
    
    if args.list_components:
        print("Available components:")
        for name, comp_config in DotfilesInstaller.COMPONENTS.items():
            print(f"  {name}: {comp_config['description']}")
        return
    
    installer = DotfilesInstaller(dry_run=args.dry_run)
    
    if args.dry_run:
        msg.custom("DRY RUN MODE - No changes will be made", color.yellow)
    
    success = installer.install_selected_components(args.components)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
