"""Binary installer for pre-built binaries from GitHub releases."""

import shutil
import tempfile
import logging
from pathlib import Path
from dataclasses import dataclass

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import Executor
from .custom.github import GitHubSSHSetup

logger = logging.getLogger(__name__)


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
        self.required_deps.extend(["wget", "tar"])

        super().__post_init__()

    def _install(self) -> bool:
        """Install the binary from archive_pattern."""
        try:
            url = self.archive_pattern.format(version=self.version)
        except ValueError as e:
            msg.error(f"    Invalid archive pattern:\n    {e}")
            return False

        msg.custom(
            f"    Installing {self.binary_name} from releases:\n    {url}", color.orange
        )

        if self.dry_run:
            display_path = str(self.installation_path).replace(str(Path.home()), "~")

            msg.custom(
                f"    Would download and install {self.binary_name} to {display_path}",
                color.cyan,
            )
            return True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            msg.custom(f"    Downloading {self.name} binary...", color.cyan)

            result = Executor().execute_cmd(
                ["wget", "-q", "-O", str(temp_path / f"{self.name}.tar.gz"), url],
                cwd=temp_path,
                message=(f"{self.name} download started"),
            )

            if not result.success:
                return False

            result = Executor().execute_cmd(
                ["tar", "-xzf", f"{self.name}.tar.gz"],
                cwd=temp_path,
                message=f"{self.name} extraction started",
            )

            if not result.success:
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
            gh_binary = Path(self.installation_path) / self.binary_name
            setup = GitHubSSHSetup(gh_binary)
            success = setup.authenticate_cli()
            if success:
                return setup.setup_ssh_key()
            return success

        return success

    def _find_and_copy_binary(
        self,
        temp_path: Path,
        target_dir: Path,
    ) -> bool:
        """Find the binary in extracted files and copy to target directory."""
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
