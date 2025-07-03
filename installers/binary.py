"""Binary installer for pre-built binaries from GitHub releases."""

import platform
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import TextIO

from messages import message as msg
from messages import color
from .base import Installer


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
        
        return True 