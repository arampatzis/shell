"""Script installer for tools that use git repositories with installer scripts."""

from datetime import datetime
from dataclasses import dataclass, field

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import execute_cmd


@dataclass(kw_only=True)
class ScriptInstaller(Installer):
    """Handles installation from git repositories with installer scripts."""

    target_dir: str = ""
    installer_script: str = ""
    installer_args: list = field(default_factory=list)
    script_url: str = ""

    def _install(self) -> bool:
        """
        Install a tool using script-based installation.
        """
        msg.custom(
            f"    Installing {self.name} from script:\n    {self.script_url}",
            color.orange
        )

        if self.dry_run:
            msg.custom(f"    Would install {self.name}")
            return True

        msg.custom(
            f"    Downloading and running {self.name} installer...",
            color.cyan
        )

        install_cmd = ['bash', '-c', f'wget -qO - {self.script_url} | bash']
        return execute_cmd(
            install_cmd,
            message = f"Starting {self.name} installation at {datetime.now()}",
        )