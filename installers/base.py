"""Base installer class for all installation types."""

from abc import ABC, abstractmethod
import logging
import shutil
from pathlib import Path
from dataclasses import dataclass, field

from .messages import message as msg
from .messages import color

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class Installer(ABC):
    """Base installer class with common functionality."""

    name: str = ""
    dry_run: bool = False
    force: bool = False
    check_cmd: str = ""
    check_path: str = ""
    installation_path: Path | str = ""
    log_file: Path | str = "install.log"
    required_deps: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Create local installation directory."""
        self.log_file = Path(self.log_file).expanduser()

        self.installation_path = Path(self.installation_path).expanduser()

        if not self.installation_path.exists():
            self.installation_path.mkdir(parents=True, exist_ok=True)
        else:
            if not self.installation_path.is_dir():
                msg.error(
                    f"Installation path {self.installation_path} is not a directory"
                )
                raise NotADirectoryError(f"{self.installation_path} is not a directory")

    @abstractmethod
    def _install(self) -> bool:
        """Install a tool."""
        raise NotImplementedError("Subclasses must implement this method")

    def install(self) -> bool:
        """Install a tool from a source to a target."""
        msg.custom(f"\n* {self.name}", color.pink)

        if self._check_installed(self.name):
            return True
        if not self._check_dependencies(self.required_deps):
            return False
        return self._install()

    def _check_installed(self, name: str) -> bool:
        """Check if the tool is already installed."""

        if shutil.which(self.check_cmd):
            if self.force:
                msg.warning(
                    f"    {self.check_cmd} already installed, forcing installation"
                )
                return False
            else:
                msg.warning(
                    f"    {self.check_cmd} already installed, skipping installation"
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
            logger.error(f"Missing dependencies: {', '.join(missing)}")
            return False
        return True
