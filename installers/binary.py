"""Binary installer for pre-built binaries from GitHub releases."""

import os
import platform
import re
import shutil
import subprocess
import tempfile
import getpass
import socket
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import TextIO

from messages import message as msg
from messages import color
from .base import Installer


def authenticate_github_cli(gh_binary: Path) -> bool:
    """Authenticate GitHub CLI with user token."""
    msg.custom("\n   Setting up GitHub CLI authentication...", color.cyan)
    msg.custom("   You'll need a GitHub Personal Access Token (PAT)", color.yellow)
    msg.custom("   To create one:", color.yellow)
    msg.custom("   1. Go to https://github.com/settings/tokens", color.yellow)
    msg.custom("   2. Click 'Generate new token (classic)'", color.yellow)
    msg.custom("   3. Select scopes: repo, workflow, read:org", color.yellow)
    msg.custom("   4. Copy the generated token", color.yellow)
    
    try:
        # Get token from user
        token = getpass.getpass(
            "   Enter your GitHub Personal Access Token [press enter to skip]: "
        )
        
        if not token.strip():
            msg.custom(
                (
                    "   No token provided. GitHub CLI authentication skipped.\n"
                    "   You can set it later with 'gh auth login'"
                ),
                color.yellow
            )
            return True
        
        # Authenticate with token
        msg.custom("   Authenticating with GitHub...", color.cyan)
        
        with open('install.log', 'a') as log_file:
            log_file.write(f"\n=== GitHub CLI authentication started ===\n")
            
            result = subprocess.run(
                [
                    str(gh_binary),
                    'auth',
                    'login',
                    '--hostname',
                    'github.com',
                    '--with-token'
                ],
                input=token.encode(),
                capture_output=True,
                text=True,
                check=True
            )
            
            log_file.write("GitHub CLI authentication completed successfully\n")
        
        msg.custom("   GitHub CLI authenticated successfully!", color.green)
        
        return True
        
    except subprocess.CalledProcessError as e:
        msg.custom(f"   GitHub CLI authentication failed: {e.stderr}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"GitHub CLI authentication failed: {e.stderr}\n")
        return False
    except KeyboardInterrupt:
        msg.custom("\n   Authentication cancelled by user.", color.yellow)
        return True
    except Exception as e:
        msg.custom(f"   Unexpected error during authentication: {e}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"Unexpected authentication error: {e}\n")
        return False


def setup_github_ssh_key(gh_binary: Path) -> bool:
    """Create and upload SSH key to GitHub."""
    msg.custom("\n   Setting up SSH key for GitHub...", color.cyan)
    
    try:
        # Get email from user with validation
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        while True:
            email = input(
                "   Enter your email for SSH key [leave blank to skip]: "
            ).strip()
            
            if not email:
                msg.custom(
                    (
                        "   No email provided. SSH key setup skipped.\n"
                        "   You can set it later with 'gh ssh-key add'"
                    ),
                    color.yellow
                )
                return True
            
            if email_pattern.match(email):
                break
            else:
                msg.custom(
                    "   Invalid email format. Please enter a valid email address.",
                    color.red
                )
        
        # Create .ssh directory if it doesn't exist
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Generate SSH key
        msg.custom("   Generating SSH key...", color.cyan)
        ssh_key_path = ssh_dir / 'github'
        
        # Check if key already exists
        if ssh_key_path.exists() or (ssh_key_path.with_suffix('.pub')).exists():
            msg.custom("   SSH key 'github' already exists.", color.yellow)
            overwrite = input("   Do you want to overwrite it? [y/N]: ").strip().lower()
            if overwrite not in ['y', 'yes']:
                msg.custom("   SSH key generation skipped.", color.yellow)
                return True
            
            # Remove existing keys
            if ssh_key_path.exists():
                ssh_key_path.unlink()
            if (ssh_key_path.with_suffix('.pub')).exists():
                (ssh_key_path.with_suffix('.pub')).unlink()
            msg.custom("   Existing SSH keys removed.", color.cyan)
        
        with open('install.log', 'a') as log_file:
            log_file.write(f"\n=== SSH key generation started ===\n")
            
            # Generate SSH key pair
            subprocess.run(
                [
                    'ssh-keygen',
                    '-t', 'ed25519',
                    '-C', email,
                    '-f', str(ssh_key_path),
                    '-N', ''  # No passphrase
                ],
                check=True,
                text=True,
                stdout=log_file,
                stderr=log_file
            )
            
            log_file.write("SSH key generated successfully\n")
        
        msg.custom("   SSH key generated successfully!", color.green)
        
        # Get IP address for key title
        try:
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True,
                text=True,
                check=True
            )
            hostname = result.stdout.strip().split()[0]  # Get first IP address
        except (subprocess.CalledProcessError, IndexError):
            hostname = socket.gethostname()  # Fallback to local hostname
        
        # Upload SSH key to GitHub
        msg.custom(f"   Uploading SSH key to GitHub as '{hostname}'...", color.cyan)
        
        with open('install.log', 'a') as log_file:
            log_file.write(f"\n=== SSH key upload started ===\n")
            
            result = subprocess.run(
                [
                    str(gh_binary),
                    'ssh-key',
                    'add',
                    str(ssh_key_path) + '.pub',
                    '--title',
                    hostname
                ],
                text=True,
                check=True,
                stdout=log_file,
                stderr=log_file
            )
            
            log_file.write("SSH key uploaded successfully\n")
        
        msg.custom("   SSH key uploaded to GitHub successfully!", color.green)
        
        # Configure SSH config for GitHub
        return configure_ssh_config()
        
    except subprocess.CalledProcessError as e:
        msg.custom(f"   SSH key setup failed: {e.stderr}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"SSH key setup failed: {e.stderr}\n")
        return False
    except KeyboardInterrupt:
        msg.custom("\n   SSH key setup cancelled by user.", color.yellow)
        return True
    except Exception as e:
        msg.custom(f"   Unexpected error during SSH key setup: {e}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"Unexpected SSH key setup error: {e}\n")
        return False


def configure_ssh_config() -> bool:
    """Configure SSH config file for GitHub."""
    try:
        ssh_config_path = Path.home() / '.ssh' / 'config'
        github_config = (
"""Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github
    IdentitiesOnly yes
"""
        )
        
        # Check if config already exists and contains GitHub config
        if ssh_config_path.exists():
            with open(ssh_config_path, 'r') as f:
                content = f.read()
            
            if 'Host github.com' in content:
                msg.custom(
                    (
                        "   GitHub SSH config already exists in ~/.ssh/config\n"
                        "   Skipping configuration."
                    ),
                    color.yellow
                )
                return True
        
        # Add GitHub config to SSH config file
        msg.custom("   Configuring SSH config for GitHub...", color.cyan)
        
        with open(ssh_config_path, 'a') as f:
            f.write(f"\n{github_config}")
        
        # Set proper permissions
        ssh_config_path.chmod(0o600)
        
        msg.custom("   SSH config configured for GitHub!", color.green)
        return True
        
    except Exception as e:
        msg.custom(f"   Failed to configure SSH config: {e}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"SSH config setup failed: {e}\n")
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
            target_display = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(f"Installing {self.name} from GitHub releases", color.cyan)
            msg.custom(
                "    Would download and install "
                f"{self.binary_name} to {target_display}", color.cyan
            )
            return True

        msg.custom(f"Installing {self.name} from GitHub releases", color.cyan)
        
        # Create local installation directory
        self.installation_path.mkdir(parents=True, exist_ok=True)
        
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
                    self.installation_path,
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
            raise FileNotFoundError(
                f"{self.binary_name} binary not found in downloaded archive"
            )
        
        target_binary = target_dir / self.binary_name
        shutil.copy2(binary_path, target_binary)
        target_binary.chmod(0o755)
        
        target_display = str(self.installation_path).replace(str(Path.home()), "~")
        msg.custom(
            f"   {self.name} installed successfully to {target_display}", color.green
        )
        msg.custom("   Detailed logs written to install.log", color.yellow)
        
        with open('install.log', 'a') as log_file:
            log_file.write(
                f"\n=== {self.name} installation completed successfully "
                "at {datetime.now()} ===\n"
            )
        
        # Handle GitHub CLI authentication if binary is "gh"
        if self.binary_name == "gh":
            auth_success = authenticate_github_cli(target_binary)
            if auth_success:
                return setup_github_ssh_key(target_binary)
            return auth_success
        
        return True 