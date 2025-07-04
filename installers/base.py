"""Base installer class for all installation types."""

from abc import ABC, abstractmethod
import logging
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import subprocess

from messages import message as msg
from messages import color


@dataclass(kw_only=True)
class Installer(ABC):
    """Base installer class with common functionality."""
    
    name: str = ""
    dry_run: bool = False
    force: bool = False
    check_cmd: str = ""
    check_path: str = ""
    required_deps: list[str] | None = None
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))
    installation_path: Path = Path.home() / "local" / "bin"
    
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

        if self.force:
            msg.custom(f"    Forcing installation of {name}", color.yellow)
            # Check if directory exists and warn user
            if self.check_path:
                check_location = Path(self.check_path).expanduser()
                if check_location.exists():
                    msg.custom(
                        f"    {name} directory exists at {check_location}.\n"
                        f"    Remove it manually before forcing installation.",
                        color.red,
                    )
                    return True
            return False

        if (self.check_cmd and shutil.which(self.check_cmd)) or self._check_path(name):
            msg.custom(f"    {name} is found in the system.", color.yellow)
            self.logger.warning(f"{name} already installed, skipping")
            return True

        return False
    
    def _check_path(self, name: str) -> bool:
        if self.check_path:
            check_location = Path(self.check_path).expanduser()
            if check_location.exists():
                self.logger.warning(
                    f"{name} already installed (directory check), skipping"
                )
                return True
        return False
    
    def _check_dependencies(self, dependencies: list[str] | None = None) -> bool:
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

            # ✅ New: log full stdout and stderr if present
            if isinstance(error, subprocess.CalledProcessError):
                log_file.write("\n--- STDOUT ---\n")
                log_file.write(error.stdout or "")
                log_file.write("\n--- STDERR ---\n")
                log_file.write(error.stderr or "")

        return False
