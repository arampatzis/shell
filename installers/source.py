"""Source installer for tools that need to be built from source code."""

import tempfile
from pathlib import Path
from dataclasses import dataclass, field
import logging

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import execute_cmd


logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class SourceInstaller(Installer):
    """Handles installation from source code."""

    version: str = ""
    archive_pattern: str = ""
    binary_name: str = ""
    build_deps: list = field(default_factory=list)
    configure_args: list = field(default_factory=list)
    run_autogen: bool = False

    def __post_init__(self):
        """Post-init setup."""

        if not self.installation_path:
            self.installation_path = Path.home() / "local/"
        else:
            self.installation_path = Path(self.installation_path).expanduser()

        self.check_cmd = self.binary_name
        self.required_deps.extend(["wget", "tar"])

        super().__post_init__()

    def _install(self) -> bool:
        """Install a tool from source code."""
        try:
            url = self.archive_pattern.format(version=self.version)
        except ValueError as e:
            msg.error(f"    Invalid archive pattern:\n    {e}")
            return False

        msg.custom(
            f"    Installing {self.binary_name} from source:\n    {url}", color.orange
        )

        if self.dry_run:
            display_path = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(
                (
                    "    Would configure, build, and install "
                    f"{self.binary_name} to {display_path}"
                ),
                color.cyan,
            )
            return True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                msg.custom(f"    Downloading {self.name} source...", color.cyan)

                result = execute_cmd(
                    ["wget", "-q", "-O", str(temp_path / f"{self.name}.tar.gz"), url],
                    cwd=temp_path,
                    message=f"{self.name} download started",
                )

                if not result.success:
                    return False

                result = execute_cmd(
                    ["tar", "-xzf", f"{self.name}.tar.gz"],
                    cwd=temp_path,
                    message=f"{self.name} source extraction started",
                )

                if not result.success:
                    return False

                # Find extracted source directory
                extracted_dirs = [
                    d
                    for d in temp_path.iterdir()
                    if d.is_dir() and d.name.startswith(self.name)
                ]
                if not extracted_dirs:
                    raise RuntimeError(
                        f"Could not find extracted {self.name} source directory"
                    )

                source_dir = extracted_dirs[0]

                # Run autogen.sh if needed
                if self.run_autogen:
                    msg.custom(f"    Running autogen.sh for {self.name}...", color.cyan)
                    result = execute_cmd(
                        ["./autogen.sh"],
                        cwd=source_dir,
                        message=f"{self.name} autogen.sh started",
                    )
                    if not result.success:
                        return False

                # Configure
                msg.custom(f"    Configuring {self.name}...", color.cyan)
                configure_cmd = ["./configure", f"--prefix={self.installation_path}"]
                if self.configure_args:
                    configure_cmd.extend(self.configure_args)

                result = execute_cmd(
                    configure_cmd,
                    cwd=source_dir,
                    message=f"{self.name} configure started",
                )

                if not result.success:
                    return False

                # Build
                msg.custom(f"    Building {self.name}...", color.cyan)
                result = execute_cmd(
                    ["make"],
                    cwd=source_dir,
                    message=f"{self.name} build started",
                )

                if not result.success:
                    return False

                # Install
                display_path = str(self.installation_path)
                display_path = display_path.replace(str(Path.home()), "~")

                msg.custom(
                    f"    Installing {self.name} to {display_path}...", color.cyan
                )
                result = execute_cmd(
                    ["make", "install"],
                    cwd=source_dir,
                    message=f"{self.name} install started",
                )

                if not result.success:
                    return False

                return True

            except Exception as e:
                logger.error(f"Error during {self.name} installation: {e}")
                msg.error(f"    Installation failed: {e}")
                return False
