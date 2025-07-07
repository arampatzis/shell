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

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import execute_cmd


def authenticate_github_cli(gh_binary: Path, log_file: Path | str = "") -> bool:
    """Authenticate GitHub CLI with user token."""
    msg.custom("\n    Setting up GitHub CLI authentication...", color.cyan)
    msg.custom("    You'll need a GitHub Personal Access Token (PAT)", color.yellow)
    msg.custom("    To create one:", color.yellow)
    msg.custom("    1. Go to https://github.com/settings/tokens", color.yellow)
    msg.custom("    2. Click 'Generate new token (classic)'", color.yellow)
    msg.custom(
        "    3. Select scopes: repo, workflow, admin:org, admin:public_key",
        color.yellow
    )
    msg.custom("    4. Copy the generated token", color.yellow)
    
    msg.custom(
        "    Paste your GitHub Personal Access Token below:",
        color.cyan
    )
    
    token = input("    Token: ")
    
    if not token.strip():
        msg.custom(
            (
                "    No token provided. GitHub CLI authentication skipped.\n"
                "    You can set it later with 'gh auth login'"
            ),
            color.yellow
        )
        return True
    
    # Authenticate with token
    msg.custom("   Authenticating with GitHub...", color.cyan)
    
    try:
        result = execute_cmd(
            [
                str(gh_binary),
                'auth',
                'login',
                '--hostname',
                'github.com',
                '--with-token'
            ],
            input=token.encode('utf-8'),
            message = f"\n=== GitHub CLI authentication started ===\n",
        )
        
        if not result:
            return False
        
        msg.custom("   GitHub CLI authenticated successfully!", color.green)
        
        return True
        
    except KeyboardInterrupt:
        msg.custom("\n   Authentication cancelled by user.", color.yellow)
        return True
    
    except Exception as e:
        msg.custom(f"   Unexpected error during authentication: {e}", color.red)
        with open(log_file, 'a') as lf:
            lf.write(f"Unexpected authentication error: {e}\n")
        return False


def setup_github_ssh_key(gh_binary: Path) -> bool:
    """Create and upload SSH key to GitHub."""
    msg.custom("\n    Setting up SSH key for GitHub...", color.cyan)
    
    try:
        # Get email from user with validation
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        while True:
            email = input(
                "    Enter your email for SSH key [leave blank to skip]: "
            ).strip()
            
            if not email:
                msg.custom(
                    (
                        "    No email provided. SSH key setup skipped.\n"
                        "    You can set it later with 'gh ssh-key add'"
                    ),
                    color.yellow
                )
                return True
            
            if email_pattern.match(email):
                break
            else:
                msg.custom(
                    "    Invalid email format. Please enter a valid email address.",
                    color.red
                )
        
        # Create .ssh directory if it doesn't exist
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Generate SSH key
        msg.custom("    Generating SSH key...", color.cyan)
        ssh_key_path = ssh_dir / 'github'
        
        # Check if key already exists
        if ssh_key_path.exists() or (ssh_key_path.with_suffix('.pub')).exists():
            msg.custom("    SSH key 'github' already exists.", color.yellow)
            overwrite = input("    Do you want to overwrite it? [y/N]: ").strip().lower()
            if overwrite not in ['y', 'yes']:
                msg.custom("    SSH key generation skipped.", color.yellow)
                return True
            
        # Remove existing keys
        if ssh_key_path.exists():
            ssh_key_path.unlink()
        if (ssh_key_path.with_suffix('.pub')).exists():
            (ssh_key_path.with_suffix('.pub')).unlink()
        msg.custom("    Existing SSH keys removed.", color.cyan)
        result = execute_cmd(
            [
                'ssh-keygen',
                '-t', 'ed25519',
                '-C', email,
                '-f', str(ssh_key_path),
                '-N', ''  # No passphrase
            ],
            message = f"\n=== SSH key generation started ===\n",
        )
        if not result:
            msg.error("   SSH key generation failed!")
            return False
        msg.custom("   SSH key generated successfully!", color.green)
        
        # Get IP address for key title

        result = execute_cmd(
                ['hostname', '-I'],
                message = f"\n=== Getting IP address ===\n",
            )
        if not result:
            msg.error("   Failed to get IP address!")
            hostname = socket.gethostname()
        else:
            hostname = result.stdout.strip().split()[0]  # Get first IP address

        
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
                capture_output=True,
                check=True
            )
            
            # Log the output
            log_file.write(f"stdout: {result.stdout}\n")
            log_file.write(f"stderr: {result.stderr}\n")
            log_file.write("SSH key uploaded successfully\n")
        
        msg.custom("   SSH key uploaded to GitHub successfully!", color.green)
        
        # Configure SSH config for GitHub
        return configure_ssh_config()
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
        msg.custom(f"   SSH key setup failed: {error_msg}", color.red)
        with open('install.log', 'a') as log_file:
            log_file.write(f"SSH key setup failed: {error_msg}\n")
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
    """Handles installation of pre-built binaries."""
    
    binary_name: str = ""
    version: str = ""
    archive_pattern: str = ""
    
    def __post_init__(self):
        """Post-init setup."""
        print(self.installation_path)
        if not self.installation_path:
            self.installation_path = Path.home() / "local/bin"
        else:
            self.installation_path = Path(self.installation_path).expanduser()
        
        self.check_cmd = self.binary_name
        self.required_deps.extend(['wget', 'tar'])
        
        super().__post_init__()
    
    def _install(self) -> bool:
        """Install the binary from archive_pattern."""
        try:
            url = self.archive_pattern.format(version=self.version)
        except ValueError as e:
            msg.error(f"    Invalid archive pattern:\n    {e}")
            return False
        
        msg.custom(
            f"    Installing {self.binary_name} from releases:\n    {url}",
            color.orange
        )
        
        if self.dry_run:
            display_path = str(self.installation_path).replace(str(Path.home()), "~")
            
            msg.custom(
                "    Would download and install "
                f"{self.binary_name} to {display_path}", color.cyan
            )
            return True
                
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            msg.custom(f"    Downloading {self.name} binary...", color.cyan)
            
            success = execute_cmd(
                [
                    'wget',
                    '-q',
                    '-O',
                    str(temp_path / f'{self.name}.tar.gz'),
                    url
                ],
                cwd=temp_path,
                msg = (
                    f"\n=== {self.name} download started at {datetime.now()} ===\n"
                ),
            )
            
            if not success:
                return False
            
            success = execute_cmd(
                [
                    'tar',
                    '-xzf',
                    f'{self.name}.tar.gz'
                ],
                cwd=temp_path,
                msg = f"\n=== {self.name} extraction started ===\n",
            )
            
            if not success:
                return False
            
            # Find and copy binary
            display_path = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(f"    Copying {self.name} to {display_path}...", color.cyan)
            success = self._find_and_copy_binary(
                temp_path,
                Path(self.installation_path).expanduser(),
            )
            if not success:
                return False
            
        # Handle GitHub CLI authentication if binary is "gh"
        if self.binary_name == "gh":
            target_binary = Path(self.installation_path) / self.binary_name
            success = authenticate_github_cli(target_binary, self.log_file)
            if success:
                return setup_github_ssh_key(target_binary, self.log_file)
            return success
            
        return success
    
    def _find_and_copy_binary(
        self,
        temp_path: Path,
        target_dir: Path,
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
        
        display_path = str(self.installation_path).replace(str(Path.home()), "~")
        msg.custom(
            f"    {self.name} installed successfully to {display_path}", color.green
        )
        
        return True 